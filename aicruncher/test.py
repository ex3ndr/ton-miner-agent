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
from sha256 import SHA256

# Sources
source1 = ''
with open(os.path.join(os.path.dirname(__file__),"kernels/sha256_util.cl"), "r") as rf:
    source1 += rf.read()
source1 += '\n'    
with open(os.path.join(os.path.dirname(__file__),"kernels/sha256_impl.cl"), "r") as rf:
    source1 += rf.read()    
source1 += '\n'
with open(os.path.join(os.path.dirname(__file__),"kernels/miner.cl"), "r") as rf:
    source1 += rf.read()
source2 = ''
with open(os.path.join(os.path.dirname(__file__),"kernels/miner2.cl"), "r") as rf:
    source2 += rf.read()

# Init OpenCL
platforms = cl.get_platforms()
device = cl.get_platforms()[0].get_devices()[0]
print("Found default device")
print(device)
ctx = cl.Context([device])
queue = cl.CommandQueue(ctx, device)
program1 = cl.Program(ctx, source1).build()
program2 = cl.Program(ctx, source2).build()
kernel1 = program1.do_work
kernel2 = program2.do_work

# Test Data
header = bytes(np.zeros((43,), dtype=np.uint8))
seed = bytes(np.zeros((16,), dtype=np.uint8))
# random = bytes(os.urandom(32))
random = bytes(np.zeros((32,), dtype=np.uint8))
data = np.frombuffer(header + random + seed + random + b'\x80\x00\x00\x00\x00', dtype=np.uint32)
hash = SHA256()
hash.update(bytes(data[0:16]))
init_vector = hash._h
offset = 1000000000000
internal_iterations = 100000
batchSize = 10
print("Test data:")
print(header.hex())
print(seed.hex())
print(random.hex())
print(bytes(data).hex())
print(init_vector)

# Buffers
output = np.zeros((batchSize, 32), dtype=np.uint8)
output_random = np.zeros((batchSize, 32), dtype=np.uint8)
cl_data = cl.Buffer(ctx, cl.mem_flags.COPY_HOST_PTR, hostbuf=data)
cl_output = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output.nbytes)
cl_output_random = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, output_random.nbytes)

# kernel-1
print("Kernel 1")
kernel1(queue, 
    (batchSize,), # Global Size
    None, # Local Size
    cl_data,
    cl_output,
    cl_output_random,
    np.uint64(offset),
    np.uint32(internal_iterations)
)
cl.enqueue_copy(queue, output, cl_output)
cl.enqueue_copy(queue, output_random, cl_output_random)

print("Result")
for i in range(0, batchSize):
    print(bytes(output[i]).hex() + ":" + bytes(output_random[i]).hex())

# kernel-2
print("Kernel 2")
kernel2(queue, 
    (batchSize,), # Global Size
    None, # Local Size
    np.uint32(init_vector[0]),
    np.uint32(init_vector[1]),
    np.uint32(init_vector[2]),
    np.uint32(init_vector[3]),
    np.uint32(init_vector[4]),
    np.uint32(init_vector[5]),
    np.uint32(init_vector[6]),
    np.uint32(init_vector[7]),
    cl_data,
    cl_output,
    cl_output_random,
    np.uint64(offset),
    np.uint32(internal_iterations)
)
cl.enqueue_copy(queue, output, cl_output)
cl.enqueue_copy(queue, output_random, cl_output_random)

print("Result")
for i in range(0, batchSize):
    print(bytes(output[i]).hex() + ":" + bytes(output_random[i]).hex())