import zlib
from os import PathLike
from typing import Union

from ..logger import logger


class IndexFileReader:
    def __init__(self, path: Union[str, PathLike]):
        self._data = b''
        with open(path, 'rb') as f:
            self._data = f.read()

    def __iter__(self):
        offset = 0
        comp_view = memoryview(self._data)
        logger.debug(f'read data of length {len(self._data)}')
        while len(comp_view) > 1:
            decomp = zlib.decompressobj()
            try:
                decomp_data = decomp.decompress(comp_view)
                if (tail_len := len(decomp.unconsumed_tail)) != 0:
                    raise RuntimeError(f'at 0x{offset:08x}: unexpected unused data of length {tail_len}')
            except zlib.error:
                offset += 1
                comp_view = comp_view[1:]
                continue
            comp_len = len(comp_view) - len(decomp.unused_data)
            logger.debug(f'at 0x{offset:08x}: found zlib compressed data of length {comp_len}, decompressed data of length {len(decomp_data)}')
            offset += comp_len
            comp_view = memoryview(decomp.unused_data)
            yield decomp_data
