import numpy as np
import pyopencl as cl
import pyopencl.tools
import pyopencl.array
import base64
import hashlib
import time
import os, sys, inspect
import requests
import threading
import logging
import json
import hashlib
import socket
import traceback
import uuid
import queue
import copy
import struct
import binascii

mf = cl.mem_flags
logger = logging.getLogger()
logger.setLevel(logging.INFO)
start_time = time.time()

F32 = 0xFFFFFFFF

_k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
      0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
      0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
      0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
      0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
      0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
      0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
      0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
      0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

_h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]


def _pad(msglen):
    mdi = msglen & 0x3F
    length = struct.pack('!Q', msglen << 3)

    if mdi < 56:
        padlen = 55 - mdi
    else:
        padlen = 119 - mdi

    return b'\x80' + (b'\x00' * padlen) + length


def _rotr(x, y):
    return ((x >> y) | (x << (32 - y))) & F32


def _maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def _ch(x, y, z):
    return (x & y) ^ ((~x) & z)


class SHA256:
    _output_size = 8
    blocksize = 1
    block_size = 64
    digest_size = 32

    def __init__(self, m=None):
        self._counter = 0
        self._cache = b''
        self._k = copy.deepcopy(_k)
        self._h = copy.deepcopy(_h)

        self.update(m)

    def _compress(self, c):
        w = [0] * 64
        w[0:16] = struct.unpack('!16L', c)

        for i in range(16, 64):
            s0 = _rotr(w[i-15], 7) ^ _rotr(w[i-15], 18) ^ (w[i-15] >> 3)
            s1 = _rotr(w[i-2], 17) ^ _rotr(w[i-2], 19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & F32

        a, b, c, d, e, f, g, h = self._h

        for i in range(64):
            s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            t2 = s0 + _maj(a, b, c)
            s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            t1 = h + s1 + _ch(e, f, g) + self._k[i] + w[i]

            h = g
            g = f
            f = e
            e = (d + t1) & F32
            d = c
            c = b
            b = a
            a = (t1 + t2) & F32

        for i, (x, y) in enumerate(zip(self._h, [a, b, c, d, e, f, g, h])):
            self._h[i] = (x + y) & F32

    def update(self, m):
        if not m:
            return

        self._cache += m
        self._counter += len(m)

        while len(self._cache) >= 64:
            self._compress(self._cache[:64])
            self._cache = self._cache[64:]

    def digest(self):
        r = copy.deepcopy(self)
        r.update(_pad(self._counter))
        data = [struct.pack('!L', i) for i in r._h[:self._output_size]]
        return b''.join(data)

    def hexdigest(self):
        return binascii.hexlify(self.digest()).decode('ascii')


device = cl.get_platforms()[1].get_devices()[0]
ctx = cl.Context([device])
print(device)

def get_bytes_from_file(filename):
    return open(filename, "rb").read()

print("Creating program...")
if 'XCL_EMULATION_MODE' in os.environ:
    if os.environ['XCL_EMULATION_MODE'] == "sw_emu":
        program = cl.Program(ctx, [device], [get_bytes_from_file("/home/steve/ton-miner-agent/build/miner.sw_emu.xclbin")]).build()
    else:
        program = cl.Program(ctx, [device], [get_bytes_from_file("/home/steve/ton-miner-agent/build/miner.hw_emu.xclbin")]).build()
else:
    program = cl.Program(ctx, [device], [get_bytes_from_file("/home/steve/ton-miner-agent/build/miner.awsxclbin")]).build()

print("Creating kernel...")
kernel = cl.Kernel(program, "do_work")
print("Creating queue...")
queue = cl.CommandQueue(ctx, device)

print("Loading config...")
def load_config():
    while True:
        try:
            resp = requests.get("http://64.225.102.108:3000/params", timeout=5)
            data = resp.json()
            key = data['id']
            ref = data['ref']
            header = b'\x00\xF2' + base64.b64decode(data['header'])
            seed = base64.b64decode(data['seed'])
            random = base64.b64decode(data['random'])
            data = header + random + seed + random
            data_padded = data + b'\x00\x00\x00\x00\x00'
            return {'key': key, 'header': header, 'ref': ref, 'seed': seed, 'random': random, 'data': data_padded, 'source': data, 'offset':0, 'lock': threading.Lock()}
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.warn("Config load error");
            time.sleep(5)
            continue
        break

# config = load_config()
# print(len(config['header']))
# print(len(config['seed']))

config = {
    'header': bytes(np.zeros((43,), dtype=np.uint8)),
    'seed': bytes(np.zeros((16,), dtype=np.uint8))
}


# Execute
print("Starting execution")
start = time.time()
batchSize = 1
repeats = 1
internal_iterations = 1000000
offset = 0
# random = b'\xe3\xa0\x06k\xfcW\x99\xd4\xbeLX(\\\xdf\xfcP\xd2\x81m\x1au[\x1b\xbc\x877\x1c.\xf3\xf2\x84v'
random = bytes(np.zeros((batchSize, 32), dtype=np.uint8))
# print(os.urandom(32))
data = np.frombuffer(config['header'] + random + config['seed'] + random + b'\x00\x00\x00\x00\x00', dtype=np.uint32)
# print(data)
output = np.zeros((batchSize, 32), dtype=np.uint8)
output_random = np.zeros((batchSize, 32), dtype=np.uint8)
res = None
res_random = None
cl_data = cl.Buffer(ctx, cl.mem_flags.COPY_HOST_PTR, hostbuf=data)
cl_output = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output.nbytes)
cl_output_random = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output_random.nbytes)

# Prepare
def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]
m = SHA256()
m.update(bytes(data[0:16]))
# print(swap32(m._h[0]))
# print(m._h[0])
# print(data)
# print(m.digest())

def buildHash(data):
    m = hashlib.sha256()
    m.update(data)
    return m.digest()
# print(buildHash(bytes(data[16])))


print("Executing")
start = time.time()
kernel(queue, (batchSize,), (1,), 
    np.uint32(m._h[0]),
    np.uint32(m._h[1]),
    np.uint32(m._h[2]),
    np.uint32(m._h[3]),
    np.uint32(m._h[4]),
    np.uint32(m._h[5]),
    np.uint32(m._h[6]),
    np.uint32(m._h[7]),
    cl_data, 
    cl_output, 
    cl_output_random,
    np.uint64(offset), 
    np.uint32(internal_iterations))
cl.enqueue_copy(queue, output, cl_output)
cl.enqueue_copy(queue, output_random, cl_output_random)
end = time.time()
print("Collecting")
print((batchSize * internal_iterations)/(end - start))

for i in range(0, batchSize):
    print(bytes(output_random[i]).hex())
    print(bytes(output[i]).hex())
    # print(bytes(data).hex())
    # print((config['header'] + bytes(output_random[i]) + config['seed'] + bytes(output_random[i])).hex())
    print(buildHash(config['header'] + bytes(output_random[i]) + config['seed'] + bytes(output_random[i])).hex())

# from pynq import Overlay
# overlay = Overlay("/home/centos/ton-miner-agent/build/hello_world.aws.xclbin")