from signature import *
from gpt import *
from keydata import *

class apfs:
    global f
    global file_name
    global apfs_signature
    global vcsb_signature
    global block_size
    global MSB
    global VS
    global volume_info  # VCSB, BTOM, EBT, root_id, volume_name

    global VCSB
    global BTOM
    global EBT
    global volume_name
    global root_id

    def set_msb_addr(self):
        self.MSB=getPart(self.f)
        #self.MSB=0xC805000
        self.f.seek(self.MSB)
        data=self.f.read(0xB0)
        self.apfs_signature=struct.unpack_from(">I", data, 0x0 + 0x20)[0]
        apfs_check_signature(self.apfs_signature)
        self.block_size=struct.unpack_from("<I",data, 0x0 + 0x24)[0]

    def set_vs_addr(self):
        self.f.seek(self.MSB)
        data=self.f.read(0xB0)
        offset=struct.unpack_from("<I", data, 0x0 + 0xA0)[0]
        self.f.seek(self.MSB+offset*self.block_size)
        data=self.f.read(self.block_size)
        offset=struct.unpack_from("<I", data, 0x0 + 0x30)[0]
        self.VS=self.MSB+self.block_size*offset

    def set_vcsb_addr(self):
        self.f.seek(self.VS)
        data=self.f.read(self.block_size)
        kd=keydata(self, self.VS)
        tmp_kd=kd.key_data
        tmp_kd=list(set([tuple(set(tmp)) for tmp in tmp_kd]))

        for i in tmp_kd:
            # 이유는 모르겠지만 tmp_kd의 첫 번째 요소가 (0, )으로 읽어와져서 
            # i[1]에서 인덱스 에러 남
            if len(i) < 2:
                continue
            self.f.seek(self.VS+self.block_size-0x28-i[1])
            self.f.read(8)
            offset=int.from_bytes(self.f.read(8)[::-1], byteorder='big')
            self.VCSB = self.MSB + self.block_size * offset
            self.set_btom_ebt_addr()
            self.volume_info.append([self.VCSB, self.BTOM, self.EBT, self.root_id, self.volume_name])

    def set_btom_ebt_addr(self):
        self.f.seek(self.VCSB)
        data=self.f.read(self.block_size)
        self.vcsb_signature=struct.unpack_from(">I", data, 0x0 + 0x20)[0]
        vcsb_check_signature(self.vcsb_signature)
        BTOM_offset=struct.unpack_from("<I", data, 0x0 + 0x80)[0]
        self.root_id=struct.unpack_from("<I", data, 0x0 + 0x88)[0]
        EBT_offset=struct.unpack_from("<I", data, 0x0 + 0x90)[0]
        self.f.seek(self.MSB+self.block_size*BTOM_offset)
        data=self.f.read(self.block_size)
        BTOM_offset=struct.unpack_from("<I", data, 0x0 + 0x30)[0]
        self.BTOM=self.MSB+self.block_size*BTOM_offset
        self.EBT=self.MSB+self.block_size*EBT_offset
        self.f.seek(self.VCSB+0x2C0)
        self.volume_name=str(self.f.read(self.block_size-0x2C0)).split('\\x00')[0][2:]

    def print_info(self):
        print("File name\t: "+self.file_name
              +"\nBlock size\t: "+hex(self.block_size)
              +"\nMSB addr\t: "+hex(self.MSB)
              +"\nVS addr\t\t: "+hex(self.VS))
        for i in self.volume_info:
            print("\nVolume name\t: "+str(i[4])
                    +"\nRoot ID\t\t: "+hex(i[3])
                    +"\nVCSB addr\t: "+hex(i[0])
                    +"\nBTOM addr\t: "+hex(i[1])
                    +"\nEBT addr\t: "+hex(i[2]))

    def __init__(self, f):
        self.f=f
        self.file_name=str(self.f)[26:-2].split('\\')[-1]
        self.volume_info=[]
        self.set_msb_addr()
        self.set_vs_addr()
        self.set_vcsb_addr()
        self.print_info()