import socket
import json
import struct
import numpy as np


def read_blob(sock, size):
    buf = ""
    while len(buf) != size:
        ret = sock.recv(size - len(buf))
        if not ret:
            raise Exception("Socket closed")
        buf += ret
    return buf

def read_long(sock):
    size = struct.calcsize("L")
    data = read_blob(sock, size)
    return struct.unpack("L", data)
    
def read_json(sock):
    # read data size first, then the whole data and decode as json
    #datasize = read_long(sock)
    #data = read_blob(sock, datasize)
    #jdata = json.load(data.decode('utf-8'))
    data = sock.recv()
    jdata = json.loads(data)
    return jdata
    
def read_image(sock):
    # read data size first, then the whole data and decode as npArray
    datasize = read_long(sock)
    data = read_blob(sock, datasize)
    jdata = np.array(data.decode('utf-8'))