import time
from .apfs import Apfs

class Type30:   # file & folder
    def set_data(
            self,
            apfs: Apfs,
            addr: int
    ):
        apfs.f.seek(addr)
        
        self.parent_folder_id = hex(int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big'))
        
        self.file_id = hex(int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big'))

        self.created_date = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.created_date = time.strftime('%c', time.gmtime((self.created_date/1000000000)))
        
        self.last_written_date = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.last_written_date = time.strftime('%c', time.gmtime((self.last_written_date/1000000000)))
        
        self.inode_change_date = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.inode_change_date = time.strftime('%c', time.gmtime((self.inode_change_date/1000000000)))
        
        self.last_access_date = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.last_access_date = time.strftime('%c', time.gmtime((self.last_access_date/1000000000)))
        
        apfs.f.read(8)  # skip unknown bytes(8)
        self.hard_link_to_file = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        
        apfs.f.read(8)  # skip unknown bytes(8)
        self.owner_permission = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        
        self.group_permission = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        
        apfs.f.read(6)  # skip unknown bytes(6)
        self.name_length1 = int.from_bytes(bytes=apfs.f.read(2)[::-1], byteorder='big')

        apfs.f.read(2)  # skip unknown bytes(2)
        self.name_length = int.from_bytes(bytes=apfs.f.read(2)[::-1], byteorder='big')   #2byte NameLength1 - NameLength2
        if self.group_permission//0x1000 == 8:
            apfs.f.read(2)  # skip unknown bytes(2)
            self.name_length2 = int.from_bytes(bytes=apfs.f.read(2)[::-1], byteorder='big')

            if self.name_length1 > self.name_length2:
                self.name_length = self.name_length1 - self.name_length2
        else:
            self.name_length2 = None
            self.name_length = self.name_length1
        self.name = str(apfs.f.read(self.name_length)).split('\\x00')[0][2:]  # '\\x00' is padding
        self.file_size = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.calculated_in_block_size = int.from_bytes(bytes=apfs.f.read(16)[::-1], byteorder='big')
        self.hard_link_to_file = str(self.hard_link_to_file)
        self.owner_permission = str(self.owner_permission)
        self.group_permission = str(self.group_permission)
        self.name_length1 = str(self.name_length1)
        self.name_length = str(self.name_length)
        self.name_length2 = str(self.name_length2)
        self.file_size = str(self.file_size)
        self.calculated_in_block_size = str(self.calculated_in_block_size)

    def get_data(self):
        return [
            self.parent_folder_id,
            self.file_id,
            self.created_date,
            self.last_written_date,
            self.inode_change_date,
            self.last_access_date,
            self.hard_link_to_file,
            self.owner_permission,
            self.group_permission,
            self.name_length1,
            self.name_length,
            self.name_length2,
            self.name,
            self.file_size,
            self.calculated_in_block_size
        ]


class Type40:   # bplist
    # unknown 2byte
    # length  2byte
    # unknown 8byte
    # unknown 5byte

    def set_data(
            self,
            apfs: Apfs,
            addr: int
    ):
        apfs.f.seek(addr)
        self.length = str(int.from_bytes(bytes=apfs.f.read(2)[::-1], byteorder='big'))

    def get_data(self):
        return [self.length]


class Type60:   # hard link
    # hard_link_count 4byte

    def set_data(
            self,
            apfs: Apfs,
            addr: int
    ):
        apfs.f.seek(addr)
        self.hard_link_count = str(int.from_bytes(bytes=apfs.f.read(4)[::-1], byteorder='big'))

    def get_data(self):
        return [self.hard_link_count]


class Type80:  # file offset, file block size
    # file_offset 8byte
    # block_count byte
    # unknown 2byte

    def set_data(
            self,
            apfs: Apfs,
            addr: int
    ):
        apfs.f.seek(addr)
        self.file_offset = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.block_count = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')

        self.file_offset = str(self.file_offset)
        self.block_count = str(self.block_count)

    def get_data(self):
        return [
            self.file_offset,
            self.block_count
        ]


class Type90:  # root node
    # node_id       8byte
    # created_date  8byte
    # unknown 2byte

    def set_data(
            self,
            apfs: Apfs,
            addr: int
    ):
        apfs.f.seek(addr)
        self.node_id = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')
        self.created_date = int.from_bytes(bytes=apfs.f.read(8)[::-1], byteorder='big')

        self.node_id = str(self.node_id)
        self.created_date = str(self.created_date)

    def get_data(self):
        return [
            self.node_id,
            self.created_date
        ]