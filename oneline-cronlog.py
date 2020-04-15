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
        next()

out.reverse()

# Print as many entries as possible so that the string is less than 75 characters
# Don't truncate the string, though!
i = 0
while len(" | ".join(out[0:i])) < MAXLEN:
    line_one = out[0:i]
    i += 1
    if i > len(out):
        break

j = i
while len(" | ".join(out[i:j])) < MAXLEN:
    line_two = out[i:j]
    j += 1
    if i > len(out):
        break

pad_width = max(len(line_one[0]), len(line_two[0]))

line_one = [x.ljust(pad_width) for x in line_one]
line_two = [x.ljust(pad_width) for x in line_two]

print("  " + " | ".join(line_one))
print("  " + " | ".join(line_two))
