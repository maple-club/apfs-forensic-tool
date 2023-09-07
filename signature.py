def apfs_check_signature(signature):
    if signature != 0x4E585342:
        print("It is not APFS")
        exit(-1)
    else:
        print("It is APFS")

def vcsb_check_signature(signature):
    if signature != 0x41505342:
        print("It is not VCSB")
        exit(-1)
    else:
        print("It is VCSB")