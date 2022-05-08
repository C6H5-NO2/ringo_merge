from dataclasses import dataclass
from os import PathLike
from typing import Dict, List, Union

from .parser import IndexPageParser
from .reader import IndexFileReader
from ..logger import logger


@dataclass
class Index:
    search_str: str = ''
    title_str: str = ''
    entry_str: str = ''
    anchor_str: str = ''
    yomi_str: str = ''


KeyTextDict = Dict[str, List[Index]]


def convert_keytext(path: Union[str, PathLike], has_yomi: bool = False) -> KeyTextDict:
    links: KeyTextDict = {}
    for decomp_data in IndexFileReader(path):
        parser = IndexPageParser(decomp_data)
        page = parser.parse()

        for container in page:
            search_str = container.items[0].search_str
            if search_str in links:
                raise SyntaxError(f'duplicated index "{search_str}"')
            links[search_str] = []

            for item in container.items:
                if search_str != item.search_str:
                    raise SyntaxError(f'"{search_str}" -> search != "{item.search_str}"')
                if len(item.entry_str) == 0 and len(item.anchor_str) != 0:
                    raise SyntaxError(f'"{search_str}" -> anchor "{item.anchor_str}" != 0')
                if not (has_yomi or len(item.yomi_str) == 0):
                    raise SyntaxError(f'"{search_str}" -> yomi "{item.yomi_str}" != 0')

                idx = Index(search_str, item.title_str, item.entry_str, item.anchor_str, item.yomi_str)
                links[search_str].append(idx)

    logger.info(f'convert {len(links)} (merged) / {sum(len(i) for i in links.values())} (split) index links')
    return links
