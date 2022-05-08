from dataclasses import dataclass
from os import PathLike
from typing import Dict, List, Union

from ..logger import logger


@dataclass
class Entry:
    headword: str
    explanation: str


BodyDict = Dict[str, List[Entry]]


def convert_body(path: Union[str, PathLike]) -> BodyDict:
    body: BodyDict = {}
    with open(path, 'rt', encoding='utf-8') as file:
        for line in file:
            tmp = line.split('\t', maxsplit=1)
            if len(tmp) != 2 or len(tmp[0]) == 0 or len(tmp[1]) == 0:
                raise SyntaxError(f'wrong body "{line}"')

            headword, explanation = tmp
            # if headword in body:
            #     raise SyntaxError(f'duplicated entry "{headword}"')

            # remove ending \n
            assert explanation[-1] == '\n', f'"{tmp}"'
            body.setdefault(headword, []).append(Entry(headword, explanation[:-1]))

    logger.info(f'convert {len(body)} (merged) / {sum(len(i) for i in body.values())} (split) entries')
    return body
