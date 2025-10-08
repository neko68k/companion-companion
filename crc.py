import math
import sys
import socket

def crc16_modbus(number):
    data = number.to_bytes(math.ceil(number.bit_length() / 8), 'big')
    crc = 0xFFFF
    polynomial = 0xA001

    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc = crc >> 1

    return crc & 0xFFFF


value = int(sys.argv[1], 16)
#crc = crc16_modbus(value)
crc = socket.ntohs(crc16_modbus(value))

print(hex(crc))
