import warnings
from dataclasses import dataclass, field
from typing import List


def int2hex(i: int, /, size: int) -> str:
    b = i.to_bytes(size, byteorder='little', signed=False)
    return ' '.join(f'{x:02x}' for x in b)


@dataclass
class IndexItem:
    nbytes: int = 0
    magic_checksum: int = 0
    """some value related to the entry"""
    entry_str_chunk_id: int = 0
    magic_flag: int = 0
    """probably related to d:parental-control & d:priority"""
    search_str_len: int = 0
    search_str: str = ''
    """i.e. d:value"""
    title_str_len: int = 0
    title_str: str = ''
    entry_str_len: int = 0
    entry_str: str = ''
    anchor_str_len: int = 0
    anchor_str: str = ''
    yomi_str_len: int = 0
    yomi_str: str = ''


@dataclass
class IndexContainer:
    nbytes: int = 0
    size: int = 0
    items: List[IndexItem] = field(default_factory=list)


class IndexPageParser:
    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def tell(self) -> int:
        return self._pos

    def read(self, size: int) -> bytes:
        prev_pos = self.tell()
        block = self._data[prev_pos: prev_pos + size]
        read_len = len(block)
        if read_len != size:
            raise EOFError(f'at 0x{prev_pos:08x}: expected to read {size} bytes, got {read_len} bytes instead')
        self._pos += read_len
        return block

    def read_as_int(self, size: int) -> int:
        block = self.read(size)
        return int.from_bytes(block, byteorder='little', signed=False)

    def read_as_str(self, size: int) -> str:
        block = self.read(size)
        return block.decode('utf-16-le')

    def parse(self) -> List[IndexContainer]:
        containers: List[IndexContainer] = []
        while True:
            try:
                container = self._parse_container()
                containers.append(container)
            except EOFError:
                break
        if self.tell() != len(self._data):
            raise RuntimeError(f'at 0x{self.tell():08x}: read stopped unexpectedly')
        return containers

    def _parse_container(self):
        container = IndexContainer()

        begin_pos = self.tell()
        container.nbytes = self.read_as_int(4)
        end_pos = self.tell() + container.nbytes

        container.size = self.read_as_int(4)

        for _ in range(container.size):
            item = self._parse_item()
            container.items.append(item)

        if (curr_pos := self.tell()) != end_pos:
            raise SyntaxError(f'at 0x{begin_pos:08x}: length mismatch. Expected end at 0x{end_pos:08x}, currently at 0x{curr_pos:08x}')

        return container

    def _parse_item(self):
        item = IndexItem()

        begin_pos = self.tell()
        item.nbytes = self.read_as_int(2)
        end_pos = self.tell() + item.nbytes

        item.magic_checksum = self.read_as_int(4)
        item.entry_str_chunk_id = self.read_as_int(4)
        item.magic_flag = self.read_as_int(2)

        item.search_str_len = self.read_as_int(2)
        if item.search_str_len == 0:
            raise SyntaxError(f'at 0x{self.tell() - 2:08x}: invalid search_str_len [{int2hex(item.search_str_len, 2)}]')
        item.search_str = self.read_as_str(item.search_str_len)

        item.title_str_len = self.read_as_int(2)
        item.title_str = self.read_as_str(item.title_str_len)

        item.entry_str_len = self.read_as_int(2)
        item.entry_str = self.read_as_str(item.entry_str_len)

        item.anchor_str_len = self.read_as_int(2)
        item.anchor_str = self.read_as_str(item.anchor_str_len)

        item.yomi_str_len = self.read_as_int(2)
        item.yomi_str = self.read_as_str(item.yomi_str_len)

        if (curr_pos := self.tell()) != end_pos:
            raise SyntaxError(f'at 0x{begin_pos:08x}: length mismatch. Expected end at 0x{end_pos:08x}, currently at 0x{curr_pos:08x}')

        return item
