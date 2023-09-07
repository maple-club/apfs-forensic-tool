from keydata import *

class node:
    global node_id_offset   #list

    def set_node_id_offset(self, apfs, volume_info, kd):
        node_id_offset=[]
        for i in kd.key_data:
            apfs.f.seek(volume_info[1]+0x38+kd.size+i[0])
            node_id=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
            apfs_id=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
            apfs.f.seek(volume_info[1]+apfs.block_size-0x28-i[1])
            apfs.f.read(4)
            block_size=int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')
            offset=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
            node_id_offset.append([node_id, offset])
        self.node_id_offset=node_id_offset

    def __init__(self, apfs, volume_info):
        kd = keydata(apfs, volume_info[1])
        self.set_node_id_offset(apfs, volume_info, kd)