#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
