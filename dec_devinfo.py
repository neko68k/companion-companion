#!/usr/bin/python3

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


import os
import sys
import base64
import json
from hashlib import md5
from Crypto.Cipher import AES

# Function to decrypt platform device config information
keycode = "3f5e1a2b4c6d7e8f9a0b1c2d3e4f5a6b"

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(aes.decrypt(encrypted[16:]))
    stringData = pt.decode('utf-8')
    data = json.loads(stringData)
    return data

def DevInfo():
    # NOTE: uncomment to use the default install path
    # appdata_path = os.getenv('APPDATA')
    # NOTE: comment if you're not me
    appdata_path = ''
    #openstage_path = os.path.join(appdata_path, 'OpenstageAI', 'deviceConfig.json')
    #cubestage_path = os.path.join(appdata_path, 'Cubestage', 'deviceConfig.json')


    #if os.path.exists(openstage_path):
    #    config_path = openstage_path
    #elif os.path.exists(cubestage_path):
    #    config_path = cubestage_path
    #else:
    #    raise FileNotFoundError(f"deviceConfig.json not found in paths:\n{openstage_path}\n{cubestage_path}")

    config_path = 'deviceConfig.json'
    print(config_path)


    with open(config_path, 'r') as file:
        j = json.load(file)

    cyphertext = j['config']
    password = keycode.encode()
    config = decrypt(cyphertext, password)

    with open('deviceConfig.json', 'w+') as file:
        json.dump(config, file, indent=4)

    return


