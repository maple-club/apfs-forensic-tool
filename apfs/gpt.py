'''
Original Code
https://github.com/ceph/simplegpt/blob/master/simplegpt.py
modified by ncw809
'''

import collections
import struct
import uuid

from typing import TextIO, NamedTuple, List, Tuple

# TODO use zlib.crc32

# http://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_table_header_.28LBA_1.29
from pip._vendor.msgpack.fallback import xrange

GPT_HEADER_FORMAT = \
'''
8s signature
4s revision
L header_size
L crc32
4x _
Q current_lba
Q backup_lba
Q first_usable_lba
Q last_usable_lba
16s disk_guid
Q part_entry_start_lba
L num_part_entries
L part_entry_size
L crc32_part_array
'''

# http://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_entries_.28LBA_2.E2.80.9333.29
GPT_PARTITION_FORMAT = \
'''
16s type
16s unique
Q first_lba
Q last_lba
Q flags
72s name
'''

class GPTError(Exception):
    pass  # Nothing to do at here.

def read_header(
        f,
        lba_size=512
) -> NamedTuple:
    f.seek(lba_size)  # Skip MBR

    fmt, GPTHeader = __make_fmt('GPTHeader', GPT_HEADER_FORMAT)
    data = f.read(struct.calcsize(fmt))
    header: NamedTuple = GPTHeader._make(struct.unpack(fmt, data))

    if header.signature.decode() != 'EFI PART':
        raise GPTError('Bad signature: %r' % header.signature)

    if header.revision.decode() != '\x00\x00\x01\x00':
        raise GPTError('Bad revision: %r' % header.revision)

    if header.header_size < 92:
        raise GPTError('Bad header size: %r' % header.header_size)

    # TODO check crc32
    header = header._replace(
        disk_guid = str(uuid.UUID(bytes_le=header.disk_guid)),
    )

    return header

def read_partitions(
        f,
        header,
        lba_size=512
):
    f.seek(header.part_entry_start_lba*lba_size)

    fmt, GPTPartition = __make_fmt('GPTPartition', GPT_PARTITION_FORMAT, extras=['index'])
    for idx in xrange(1, 1 + header.num_part_entries):
        data = f.read(header.part_entry_size)
        if len(data) < struct.calcsize(fmt):
            raise GPTError('Short partition entry')

        part = GPTPartition._make(struct.unpack(fmt, data) + (idx, ))

        if part.type == '\x00'*16:
            continue

        part = part._replace(
            type=str(uuid.UUID(bytes_le=part.type)),
            unique=str(uuid.UUID(bytes_le=part.unique)),
            # do C-style string termination
            # otherwise you'll see a long row of NILs for most names
            name=part.name.decode('utf-16').split('\0', 1)[0],
        )

        yield part

def __make_fmt(
        name: str,
        format: str,
        extras=[]
):
    type_and_name: List[Tuple[str, str]] = [tuple(l.split(None, 1)) for l in format.strip().splitlines()]
    fmt = ''.join(t for t, n in type_and_name)
    fmt = '<' + fmt
    tupletype: NamedTuple = collections.namedtuple(name, [n for (t, n) in type_and_name if n != '_'] + extras)

    return (fmt, tupletype)

def get_part(f):
    header = read_header(f)
    part_arr = []
    for part in read_partitions(f, header):
        if(part.first_lba == 0 or part.name == 'EFI System Partition'):
            continue
        part_arr.append([part.name, part.first_lba])

    return part_arr[0][1]*512