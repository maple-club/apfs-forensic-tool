#btom
class keydata:
    global key_data         #list
    global size

    def set_key_data(self, apfs, addr):
        apfs.f.seek(addr+0x2A)
        self.size=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
        apfs.f.seek(addr+0x38)
        key_data=[]
        for i in range(self.size//4):
            key_offset=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            data_offset=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            key_data.append([key_offset, data_offset])
        self.key_data=key_data

    def __init__(self, apfs, addr):
        self.set_key_data(apfs, addr)

#ebt, node
class keydatalen:
    global key_data_len     #list
    global size

    def set_key_data_len_offset(self, apfs, addr):
        apfs.f.seek(addr+0x2A)
        self.size=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
        apfs.f.seek(addr+0x38)
        key_data_len=[]
        for _ in range(self.size//8):
            key_offset=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            key_len=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            data_offset=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            data_len=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            key_data_len.append([key_offset, key_len, data_offset, data_len])
        self.key_data_len=key_data_len

    def __init__(self, apfs, addr):
        self.set_key_data_len_offset(apfs, addr)