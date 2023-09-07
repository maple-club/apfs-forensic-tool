from keydata import *
from datatype import *

class file:
    global file_id_offset
    global file_info
    global file_id_lst

    def set_file_id_offset(self, apfs, kdl, volume_info):
        file_id_offset=[]
        for i in kdl.key_data_len:
            apfs.f.seek(volume_info[2]+0x38+kdl.size+i[0])
            offset=int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')
            apfs.f.seek(volume_info[2]+apfs.block_size-0x28-i[2])
            apfs.f.read(8)  #unknown
            file_id=int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')
            apfs.f.read(4)  #unknown
            file_id_offset.append([file_id, offset])
        self.file_id_offset=file_id_offset

    def set_file_info(self, apfs, kdl, node_id_offset, node_id):
        if node_id_offset[0] in node_id:
            return
        else:
            node_id.append(node_id_offset[0])
        apfs.f.seek(apfs.MSB + node_id_offset[1] * apfs.block_size + 0x38 + kdl.size + kdl.key_data_len[0][0])
        tmp_file_id = int.from_bytes(apfs.f.read(7)[::-1], byteorder='big')
        type30_data = None
        type40_data = None
        type60_data = None
        type80_data = None
        type90_data = None
        for i in kdl.key_data_len:
            apfs.f.seek(apfs.MSB + node_id_offset[1] * apfs.block_size + 0x38 + kdl.size + i[0])
            file_id = int.from_bytes(apfs.f.read(7)[::-1], byteorder='big')
            file_type = int.from_bytes(apfs.f.read(1)[::-1], byteorder='big')
            if i == kdl.key_data_len[-1] or file_id != tmp_file_id:
                tmp_file_id = file_id
                if type30_data is None:
                    type30_data = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
                if type30_data[12] == '':
                    continue
                if type40_data is None:
                    type40_data = [None]
                if type60_data is None:
                    type60_data = [None]
                if type80_data is None:
                    type80_data = [None, None]
                if type90_data is None:
                    type90_data = [None, None]
                self.file_info.append(type30_data + type40_data + type60_data + type80_data + type90_data)
                type30_data = None
                type40_data = None
                type60_data = None
                type80_data = None
                type90_data = None
            if file_type == 0x30:
                file_data = type30()
                file_data.setData(apfs, apfs.MSB + node_id_offset[1] * apfs.block_size + apfs.block_size - i[2])
                type30_data = file_data.getData()
            elif file_type == 0x40:
                file_data = type40()
                file_data.setData(apfs, apfs.MSB + node_id_offset[1] * apfs.block_size + apfs.block_size - i[2])
                type40_data = file_data.getData()
            elif file_type == 0x60:
                file_data = type60()
                file_data.setData(apfs, apfs.MSB + node_id_offset[1] * apfs.block_size + apfs.block_size - i[2])
                type60_data = file_data.getData()
            elif file_type == 0x80:
                file_data = type80()
                file_data.setData(apfs, apfs.MSB + node_id_offset[1] * apfs.block_size + apfs.block_size - i[2])
                type80_data = file_data.getData()
            elif file_type == 0x90:
                file_data = type90()
                file_data.setData(apfs, apfs.MSB + node_id_offset[1] * apfs.block_size + apfs.block_size - i[2])
                type90_data = file_data.getData()

    def __init__(self, apfs, volume_info, node_id_offset):
        kdl=keydatalen(apfs, volume_info[2])
        node_id=[]
        self.set_file_id_offset(apfs, kdl, volume_info)
        self.file_info=[]
        self.file_id_lst=[]
        for i in node_id_offset:
            if i[0]==volume_info[3]:
                continue
            kdl=keydatalen(apfs, apfs.MSB+i[1]*apfs.block_size)
            self.set_file_info(apfs, kdl, i, node_id)

        dup=[]
        for i in range(len(self.file_info)):
            if self.file_info[i][1] in self.file_id_lst:
                dup.append(i)
            else:
                self.file_id_lst.append(self.file_info[i][1])

        dup.reverse()
        for i in dup:
            del self.file_info[i]