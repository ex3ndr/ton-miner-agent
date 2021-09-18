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
mf = cl.mem_flags
logger = logging.getLogger()
logger.setLevel(logging.INFO)
start_time = time.time()

device = cl.get_platforms()[0].get_devices()[0]
ctx = cl.Context([device])
print(device)

def get_bytes_from_file(filename):
    return open(filename, "rb").read()

print("Creating program...")
if os.environ['XCL_EMULATION_MODE'] == "sw_emu":
    program = cl.Program(ctx, [device], [get_bytes_from_file("/home/centos/ton-miner-agent/build/miner.sw_emu.xclbin")]).build()
else:
    program = cl.Program(ctx, [device], [get_bytes_from_file("/home/centos/ton-miner-agent/build/miner.hw_emu.xclbin")]).build()

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
internal_iterations = 10
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

print("Executing")
cl.enqueue_copy(queue, cl_data, data)
kernel(queue, (batchSize,), (1,), cl_data, cl_output, cl_output_random, np.uint64(offset), np.uint32(internal_iterations))
cl.enqueue_copy(queue, output, cl_output)
cl.enqueue_copy(queue, output_random, cl_output_random)
print("Collecting")

def buildHash(data):
    m = hashlib.sha256()
    m.update(data)
    return m.digest()
for i in range(0, batchSize):
    print(bytes(output_random[i]).hex())
    print(bytes(output[i]).hex())
    # print(bytes(data).hex())
    # print((config['header'] + bytes(output_random[i]) + config['seed'] + bytes(output_random[i])).hex())
    print(buildHash(config['header'] + bytes(output_random[i]) + config['seed'] + bytes(output_random[i])).hex())

# from pynq import Overlay
# overlay = Overlay("/home/centos/ton-miner-agent/build/hello_world.aws.xclbin")