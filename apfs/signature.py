from .exceptions import *


def apfs_check_signature(signature):
    return signature == 0x4E585342


def vcsb_check_signature(signature):
    return signature == 0x41505342
