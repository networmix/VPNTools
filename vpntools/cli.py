#! /root/env/env/bin/python3
from argparse import ArgumentParser
from typing import Dict, Union

from vpntools.workflows import DEPLOY_WIREGUARD_WF, STATUS_WF

cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")


def argument(*argparse_args, **argparse_kwargs):
    return argparse_args, argparse_kwargs


def subcommand(*subparser_args, parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for args, kwargs in subparser_args:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)

    return decorator


@subcommand(argument("vpn_yaml"))
def status(args: Dict[str, Union[str, int, float]]):
    """Get status"""
    STATUS_WF.run(args=args)


@subcommand(argument("vpn_yaml"))
def deploy_wg(args: Dict[str, Union[str, int, float]]):
    """Deploy Wireguard"""
    DEPLOY_WIREGUARD_WF.run(args=args)


def main() -> None:
    args = cli.parse_args()

    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(vars(args))


if __name__ == "__main__":
    main()
