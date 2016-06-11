__author__ = 'Kaundur'
import struct

import binascii

# http://stevehanov.ca/blog/index.php?id=143

file = 'Simplex.ttf'

# TODO
# Should build custom data reader with functions built in
# Do checksum check

def get_string(f):
    return f.read(4)

def uint16(f):
    val = f.read(2)
    return binascii.hexlify(val)


def uint32(f):
    val = f.read(4)
    return binascii.hexlify(val)
    #print binascii.hexlify(val)


bytes = open(file, mode='rb').read()

val = bytes[0:3]
print binascii.hexlify(val)

print int('0001a278', 16)

val = bytes[107128: 107128+4]
print binascii.hexlify(val), 'hex'
val = bytes[107128+5: 107128+9]
print binascii.hexlify(val), 'hex'
#print int(val, 16)

with open(file, mode='rb') as f:


    # True type - 0x74727565 and 0x00010000
    # typ1 x74797031
    # OTTO x4F54544F
    # Should be looking for 0x00010000
    print 'scalar', uint32(f)

    # Convert hex to int
    num_tables = int(uint16(f), 16)
    print 'tables', num_tables
    print 'search range', uint16(f)

    print 'entry selector', uint16(f)

    print 'range shift', uint16(f)

    tables = {}

    # 14 tables
    for i in range(num_tables):
        table_tag = get_string(f)
        tables[table_tag] = {}

        tables[table_tag]['CheckSum'] = uint32(f)
        tables[table_tag]['Offset'] = uint32(f)
        tables[table_tag]['Length'] = uint32(f)

    print tables


# https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html#Overview
# First - offset table
#Type	Name	Description
# uint32	scaler type	A tag to indicate the OFA scaler to be used to rasterize this font; see the note on the scaler type below for more information.
# uint16	numTables	number of tables
# uint16	searchRange	(maximum power of 2 <= numTables)*16
# uint16	entrySelector	log2(maximum power of 2 <= numTables)
# uint16	rangeShift	numTables*16-searchRange