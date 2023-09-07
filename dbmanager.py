import sqlite3

class dbmanager:

    def file_info_insert(self, file_info, c, volume_info):
        #for info in file_info:
        c.executemany("INSERT INTO "+volume_info[4]+" VALUES(?, ?, ?, ?, ?, ?, ? \
                        , ?, ?, ?, ?, ?, ?, ?\
                        , ?, ?, ?, ?, ?, ?, ?);", file_info) # (info,))

    def __init__(self, file_info, volume_info):
        conn=sqlite3.connect("apfs.db", isolation_level=None)
        c=conn.cursor()
        c.execute("CREATE TABLE "+volume_info[4]+" \
                    (ParentFolderID text, \
                    FileID text PRIMARY KEY, \
                    CreatedDate text, \
                    LastWrittenDate text, \
                    iNodeChangeDate text, \
                    LastAccessDate text, \
                    HardlinktoFile text, \
                    OwnPermission text, \
                    GroupPermission text, \
                    NameLength1 text, \
                    NameLength text, \
                    NameLength2 text, \
                    Name text, \
                    FileSize text, \
                    CalculatedinBlockSize text, \
                    Length text, \
                    HardLinkCount text, \
                    FileOffset text, \
                    BlockCount text, \
                    NodeID text, \
                    CreatedDate2 text)")


        c.execute("INSERT INTO "+volume_info[4]+" (FileID, Name) VALUES('0x1', '"+volume_info[4]+"');")
        #conn.commit()

        self.file_info_insert(file_info, c, volume_info)
        conn.close()