#!/usr/bin/env python3

import re
from datetime import datetime
import sys

# Script to print pretty versions of the interesting parts of the cron log
# Mainly built for conky integration
# It's called oneline-croglog but actually it prints two lines now
# Don't @ me


PATH = '/var/log/cron.log'  # Path to CRON log
INTERESTING_USERS = ['colin']  # List of users to monitor
PRINT_LINES = 2  # Number of lines to print

# Max length of the output string
try:
    MAXLEN = int(sys.argv[1])  # Fix argument is line length
except ValueError:
    MAXLEN = 75  # Otherwise make it 75

patterns = ['(' + user + ').*(CMD)' for user in INTERESTING_USERS]
pattern = "|".join(patterns)

kept = []

# Open the file, read as a list and strip the whitespace/newlines
# Only keep the lines that have a match to USERS
with open(PATH, "r") as log:
    for line in log:
        if re.search(pattern, line):
            kept.append(line.rstrip())

# If the cronlog is empty, check the recently cached log at cronlog.1
if not len(kept):
    with open(PATH + ".1", "r") as log:
        for line in log:
            if re.search(pattern, line):
                kept.append(line.rstrip())


# Split each line on space or () or /
cleaned = []
for line in kept:
    script_info = tuple(re.split("[ ()/]", line))
    cleaned.append(script_info)

# Clean it up and format it
out = []
for line in cleaned:
    try:
        line = [x for x in line if x != '']
        month, day, time, _, _, user, _, *path = line
        year = datetime.now().year  # CRON log doesn't keep the year but it's safe to assume it's this year
        dt = "{0}-{1}-{2} {3}".format(year, month, day, time)
        dt = datetime.strptime(dt, '%Y-%b-%d %H:%M:%S')
        time_out = dt.strftime('%a %H:%M')  # Print as Dow HH:MM (Wed, 03:01)
        out.append('{0} - {1}'.format(time_out, path[-1]))
    except ValueError:
        out.append('???')

out.reverse()  # So newest entries are first


lines = [[] for i in range(0, PRINT_LINES)]
i = j = 0

# For each line, find the number of entries that can be printed without surpassing MAXLEN characters
for k in range(0, PRINT_LINES):
    while len(" | ".join(out[i:(j+1)])) < MAXLEN:
        j += 1
        lines[k] = out[i:j]
        if j > len(out):
            break
    i = j


# Determine column width for padding
col_count = max([len(line) for line in lines])
col_widths = [max([len(lines[row][col]) for row in range(0, len(lines))])
                                        for col in range(col_count)]

# Pad each column and then print it
for line in lines:
    for i in range(0, len(line)):
        line[i] = line[i].ljust(col_widths[i])
    print("  " + " | ".join(line))
