############################################
# This is for CRC-8 Maxim/Dallas Algorithm
# Improved with less variable and functions
# Supports both Python3.x and Python2.x
# Has append and check functions
# When standalone, can read from either arguments or stdin
# Writes to stdout cleaner
# http://gist.github.com/eaydin
############################################

def crc8calc(incoming):
    msg = bytearray(incoming.encode(encoding="ascii"))
    check = 0
    for i in msg:
        check = AddToCRC(i, check)
    return check

def AddToCRC(b, crc):
    if (b < 0):
        b += 256
    for i in range(8):
        odd = ((b^crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if (odd):
            crc ^= 0x8C # this means crc ^= 140
    return crc
