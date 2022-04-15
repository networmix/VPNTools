import re
import logging
from typing import Any, Dict, List, Callable, Tuple, Optional, Union, Match


logger: logging.Logger = logging.getLogger()


class TextParser:
    def __init__(
        self,
        regexp_lst: List[str],
        line_proc: Optional[Callable[[str], str]] = None,
        line_parser: Optional[
            Callable[[Match], Tuple[str, Union[str, int, float]]]
        ] = None,
    ) -> None:
        self._regexp_lst = regexp_lst
        self._line_proc = line_proc if line_proc else lambda x: x.strip()
        self._line_parser = (
            line_parser
            if line_parser
            else lambda x: (x.group(1).strip(), x.group(2).strip())
        )
        self._cur_obj: Dict[Any, Any] = {}
        self._stack: List[Dict[Any, Any]] = [self._cur_obj]

    def _reset(self) -> None:
        self._cur_obj = {}
        self._stack = [self._cur_obj]

    def parse_text(self, text: str) -> Dict[Any, Any]:
        self._reset()

        for line in text.splitlines():
            line = self._line_proc(line)
            if line:
                self._parse_line(line)
        return self._stack[0]

    def _parse_line(self, line: str) -> None:
        for idx, pattern in enumerate(self._regexp_lst):
            logger.debug(
                "_parse_line:\nline: '%s'\npattern[%s]: '%s'", line, idx, pattern
            )
            match = re.match(pattern, line)

            if match:
                logger.debug("_parse_line: Match!")

                if idx == len(self._regexp_lst) - 1:
                    # final level, parsing line
                    if (
                        len(self._stack) == len(self._regexp_lst) - 1
                        and self._stack[-1]
                    ):
                        # block tags are populated
                        key, value = self._line_parser(match)
                        self._cur_obj[key] = value

                else:
                    # not final yet, parsing a block tag
                    key = match.group(1).strip()

                    if idx == len(self._stack) - 1:
                        # keeping block level
                        self._stack[-1].setdefault(key, {})
                        self._cur_obj = self._stack[-1][key]

                    elif idx > len(self._stack) - 1:
                        # increasing block level
                        new_obj = {}
                        self._cur_obj[key] = new_obj
                        self._stack.append(self._cur_obj)
                        self._cur_obj = new_obj

                    elif idx < len(self._stack) - 1:
                        # decreasing block level
                        self._stack.pop()
                        self._stack[-1].setdefault(key, {})
                        self._cur_obj = self._stack[-1][key]
                break
