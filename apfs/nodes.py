from .keydata import KeyData
from .apfs import Apfs

from typing import List, Any


class Node:
    # global node_id_offset   #list

    def __init__(
            self,
            apfs: Apfs,
            volume_info: List[Any]
    ):
        kd = KeyData(apfs, volume_info[1])
        self.node_id_offset = None
        self.set_node_id_offset(apfs, volume_info, kd)

    def set_node_id_offset(
            self,
            apfs: Apfs,
            volume_info: List[Any],
            kd: KeyData
    ):
        node_id_offset = []
        for key_offset, data_offset, in kd.key_data:
            apfs.f.seek(volume_info[1] + 0x38 + kd.size + key_offset)
            node_id = int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
            # apfs.f.read(8)  # apfs_id
            apfs_id = int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
            apfs.f.seek(volume_info[1] + apfs.block_size - 0x28 - data_offset)
            apfs.f.read(4)
            # apfs.f.read(4)  # block_size
            block_size = int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')
            offset = int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')

            node_id_offset.append((node_id, offset))
        
        self.node_id_offset = node_id_offset
