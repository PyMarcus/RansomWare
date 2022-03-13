import struct
import urllib.request
import sys

x: int = struct.calcsize('P') * 8
print(x)