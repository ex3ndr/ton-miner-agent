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

# Test Data
header = bytes(np.zeros((43,), dtype=np.uint8))
seed = bytes(np.zeros((16,), dtype=np.uint8))
random = bytes(os.urandom(32))
data = np.frombuffer(header + random + seed + random + b'\x80\x00\x00\x00\x00', dtype=np.uint32)