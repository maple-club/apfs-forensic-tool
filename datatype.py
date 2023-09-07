import time

class type30:   #file & folder
    global ParentFolderID   #8byte
    global FileID           #8byte
    global CreatedDate      #8byte
    global LastWrittenDate  #8byte
    global iNodeChangeDate  #8byte
    global LastAccessDate   #8byte
    #unknown 8byte
    global HardlinktoFile   #8byte
    #unknown 8byte
    global OwnPermission    #4byte
    global GroupPermission  #4byte
    #unknown 6byte
    global NameLength1      #2byte
    #unknown 2byte
    global NameLength       #2byte NameLength1 - NameLength2
    #unknown 2byte
    global NameLength2
    global Name
    
    global FileSize         #8byte
    global CalculatedinBlockSize   #16byte FileSize에 맞춘 블록 사이즈
    #filesize 8byte

    def setData(self, apfs, addr):
        apfs.f.seek(addr)
        self.ParentFolderID=hex(int.from_bytes(apfs.f.read(8)[::-1], byteorder='big'))
        self.FileID=hex(int.from_bytes(apfs.f.read(8)[::-1], byteorder='big'))
        self.CreatedDate=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.CreatedDate=time.strftime("%c", time.gmtime((self.CreatedDate/1000000000)))
        self.LastWrittenDate=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.LastWrittenDate=time.strftime("%c", time.gmtime((self.LastWrittenDate/1000000000)))
        self.iNodeChangeDate=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.iNodeChangeDate=time.strftime("%c", time.gmtime((self.iNodeChangeDate/1000000000)))
        self.LastAccessDate=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.LastAccessDate=time.strftime("%c", time.gmtime((self.LastAccessDate/1000000000)))
        apfs.f.read(8)   #filter unknown
        self.HardlinktoFile=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        apfs.f.read(8)  # filter unknown
        self.OwnPermission=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.GroupPermission=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        apfs.f.read(6)  # filter unknown
        self.NameLength1=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
        apfs.f.read(2)  # filter unknown
        self.NameLength=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')   #2byte NameLength1 - NameLength2
        if self.GroupPermission//0x1000==8:
            apfs.f.read(2)  # filter unknown
            self.NameLength2=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')
            if self.NameLength1 > self.NameLength2:
                self.NameLength=self.NameLength1-self.NameLength2
        else:
            self.NameLength2=None
            self.NameLength=self.NameLength1
        self.Name=str(apfs.f.read(self.NameLength)).split('\\x00')[0][2:]
        self.FileSize=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.CalculatedinBlockSize=int.from_bytes(apfs.f.read(16)[::-1], byteorder='big')
        self.HardlinktoFile=str(self.HardlinktoFile)
        self.OwnPermission=str(self.OwnPermission)
        self.GroupPermission=str(self.GroupPermission)
        self.NameLength1=str(self.NameLength1)
        self.NameLength=str(self.NameLength)
        self.NameLength2=str(self.NameLength2)
        self.FileSize=str(self.FileSize)
        self.CalculatedinBlockSize=str(self.CalculatedinBlockSize)

    def getData(self):
        return [self.ParentFolderID,
                self.FileID,
                self.CreatedDate,
                self.LastWrittenDate,
                self.iNodeChangeDate,
                self.LastAccessDate,
                self.HardlinktoFile,
                self.OwnPermission,
                self.GroupPermission,
                self.NameLength1,
                self.NameLength,
                self.NameLength2,
                self.Name,
                self.FileSize,
                self.CalculatedinBlockSize]

class type40:   #bplist
    #unknown 2byte
    global Length           #2byte
    #unknown 8byte
    #unknown 5byte

    def setData(self, apfs, addr):
        apfs.f.seek(addr)
        self.Length=int.from_bytes(apfs.f.read(2)[::-1], byteorder='big')

        self.Length=str(self.Length)

    def getData(self):
        return [self.Length]

class type60:   #HardLink
    global HardLinkCount    #4byte

    def setData(self, apfs, addr):
        apfs.f.seek(addr)
        self.HardLinkCount=int.from_bytes(apfs.f.read(4)[::-1], byteorder='big')

        self.HardLinkCount=str(self.HardLinkCount)

    def getData(self):
        return [self.HardLinkCount]

class type80:   #file offset, file block size
    global FileOffset       #8byte
    global BlockCount       #8byte
    #unknown 2byte

    def setData(self, apfs, addr):
        apfs.f.seek(addr)
        self.FileOffset=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.BlockCount=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')

        self.FileOffset=str(self.FileOffset)
        self.BlockCount=str(self.BlockCount)

    def getData(self):
        return [self.FileOffset,
                self.BlockCount]

class type90:   #rootnode
    global NodeID           #8byte
    global CreatedDate      #8byte
    #unknown 2byte

    def setData(self, apfs, addr):
        apfs.f.seek(addr)
        self.NodeID=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')
        self.CreatedDate=int.from_bytes(apfs.f.read(8)[::-1], byteorder='big')

        self.NodeID=str(self.NodeID)
        self.CreatedDate=str(self.CreatedDate)

    def getData(self):
        return [self.NodeID,
                self.CreatedDate]