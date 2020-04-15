#!/usr/bin/env python3

from sys import argv
from requests import get


URL = 'http://myexternalip.com/raw'
try:
    PADDING = int(argv[1]) + (3 * 4 + 3)
except (ValueError, IndexError) as error:
    PADDING = 3 * 4 + 3

ip = get(URL).text

print(ip.rjust(PADDING))
