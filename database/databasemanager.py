import sqlite3
import tempfile

from analysis.analysis import *

class DatabaseManager:
    APFS_TABLE_NAME = 'apfs'
    METADATA_TABLE_NAME = 'metadata'

    def __new__(cls):
        # instance라는 속성이 cls에 없다면
        if not hasattr(cls, '_instance'):
            cls._instance = super(DatabaseManager, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        # instance 생성
        cls = type(self)
        if not hasattr(cls, '_initialized'):
            self.tempfile = tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=".db")
            self.conn = sqlite3.connect(self.tempfile.name, isolation_level=None)
            self.cursor = None
            self.init_tables()
            cls._initialized = True

    def init_tables(self) -> bool:
        # 기본정보 테이블 key-value 구조로 하나
        # cursor = self.conn.cursor()
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                f'''
                CREATE TABLE `{self.METADATA_TABLE_NAME}` ( 
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                '''
            )

            self.cursor.execute(
                f'''
                CREATE TABLE `{self.APFS_TABLE_NAME}` (
                    parent_folder_id TEXT,
                    file_id TEXT PRIMARY KEY,
                    created_date TEXT,
                    last_written_date TEXT,
                    inode_change_date TEXT,
                    last_access_date TEXT,
                    hard_link_to_file TEXT,
                    owner_permission TEXT,
                    group_permission TEXT,
                    name_length1 TEXT,
                    name_length TEXT,
                    name_length2 TEXT,
                    name TEXT,
                    file_size TEXT,
                    calculated_in_block_size TEXT,
                    length TEXT,
                    hard_link_count TEXT,
                    file_offset TEXT,
                    block_count TEXT,
                    node_id TEXT,
                    created_date2 TEXT
                )
                '''
            )    
            
        except sqlite3.OperationalError:
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True
        finally:
            self.cursor.close()


    def insert_analysis_data(
        self,
        file_info,
    ) -> bool:
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(
                f'''
                INSERT
                INTO `{self.APFS_TABLE_NAME}` (
                    file_id,
                    name
                )
                VALUES (
                    \'0x1\',
                    \'{self.APFS_TABLE_NAME}\'
                )
                '''
            )

            self.cursor.executemany(
                f'''
                INSERT
                INTO {self.APFS_TABLE_NAME}
                VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?
                )
                ''',
                file_info
            )
        except sqlite3.OperationalError:
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True
        finally:
            self.cursor.close()


    def insert_metadata(
            self,
            key: str,
            value: str
    ) -> bool:
        self.cursor = self.conn.cursor()
        try:
            query = \
            f'''
            INSERT
            INTO {self.METADATA_TABLE_NAME} (
                key,
                value
            )
            VALUES (
                \'{key}\',
                \'{value}\'
            )'''
            self.cursor.execute(query)
        except sqlite3.OperationalError:
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True
        finally:
            self.cursor.close()

    def get_temp_file_path(self) -> str:
        return self.tempfile.name

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        self.tempfile.close()
