import logging
import inspect
from os import path
from typing import Any, Callable, Dict, Iterable
from types import ModuleType

import yaml


logger = logging.getLogger(__name__)


def load_resource(filename: str, resource_module: ModuleType) -> str:
    logger.debug("Loading a resource file %r.%s", resource_module, filename)
    with open(get_resource_path(filename, resource_module), "r", encoding="utf8") as fd:
        return fd.read()


def get_resource_path(filename: str, resource_module: ModuleType) -> str:
    logger.debug(
        "Obtaining the full path of a resource file %r.%s", resource_module, filename
    )
    return path.join(path.dirname(resource_module.__file__), filename)


def yaml_to_dict(yaml_str: str) -> Dict:
    return yaml.safe_load(yaml_str)


def filter_dict(old_dict: Dict[Any, Any], keys: Iterable[Any]) -> Dict[Any, Any]:
    return {key: old_dict[key] for key in keys if key in old_dict}


def filter_kwargs(func: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    return filter_dict(kwargs, inspect.getfullargspec(func)[0])
