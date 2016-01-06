#!/usr/bin/env python

#==============================================================================#
#                                                                              #
# Downloads the schedule from the Game Done Quick site and create a CSV file   #
# for importing in the google calendar                                         #
#                                                                              #
#==============================================================================#

#== IMPORT ====================================================================#

from __future__ import with_statement
import datetime as dt
import hashlib
import os
import re
import sys

#== CONST/CONF ================================================================#

# Whether all messages should be printed or not
VERBOSE = True

# Base directory
BASE_DIR = '/media/data/ubuntu/github/GDQ-iCal-generator'

# Generated iCal file
CALENDAR_FILE = BASE_DIR + '/cal.ical.ics'
# Calendar's name
CALENDAR_NAME = 'AGDQ 2016'

# Source of the calendar
CALENDAR_URL = 'https://gamesdonequick.com/schedule'
# The calendar is downloaded to this file
TEMP_FILE = '/tmp/temp_cal.html'
# Directory where data is stored between runs
VAR_DIR = BASE_DIR + '/var'
# File where the calendar's current version is stored
VERSION_FILE = VAR_DIR + '/gdq_cal_version'
# Hash of the previously downloaded calendar, to decided whether to update
HASH_FILE = VAR_DIR + '/hash.sha512'

#== HELPER FUNCTIONS ==========================================================#

def print_verb(s):
    global VERBOSE
    if VERBOSE:
        print s

def skip_token(tk, f):
    line = f.readline()
    if line.find(tk) != 0:
        print line
    assert line.find(tk) == 0

#== MAIN ======================================================================#

# Download the page
# TODO Use urllib to get the job done!
os.system("wget -q -O" + TEMP_FILE + " " + CALENDAR_URL)
if not os.path.isfile(TEMP_FILE):
    print_verb('Failed to Download the calendar! Exiting...')
    sys.exit(1)
else:
    print_verb('Schedule successfully downloaded into {:s}'.format(TEMP_FILE))

# Calculate its SHA 512
alg = hashlib.sha512()
with open(TEMP_FILE, 'rt') as fin:
    for line in fin:
        alg.update(line)
dgst = alg.digest()

# Check if the SHA differs from the previously stored one
str_hash = ''.join("{:02x}".format(ord(c)) for c in dgst)
print_verb('Downloaded schedule\'s hash (SHA 512): {:s}'.format(str_hash))
if os.path.isfile(HASH_FILE):
    with open(HASH_FILE, 'rt') as fin:
        prev_str_hash = fin.readline()
        if str_hash == prev_str_hash:
            print_verb('Schedule not updated! Exiting...')
            sys.exit(0)
        else:
            print_verb('Got a new schedule! Updating...')
else:
    print_verb('No previous hash! Generating first calendar...')

# Retrieve the current version and update it
UPDATE_VERSION = 0
if os.path.isfile(VERSION_FILE):
    with open(VERSION_FILE, "rt") as fin:
        UPDATE_VERSION = int(fin.readline())
        UPDATE_VERSION += 1
print_verb('Current calendar version: {:d}'.format(UPDATE_VERSION))

# Compile the Regex to retrieve the content of a table's cell
td_re = re.compile(r'<td.*?>(.*?)</td>')

# Current time in UTC
dt_now = dt.datetime.utcnow()

# Open both input and output files
print_verb('Reading schedule and generating calendar...')
with open(TEMP_FILE, "rt") as fin:
    with open(CALENDAR_FILE, "wt") as fout:
        # Write calendar's header
        fout.write('BEGIN:VCALENDAR\n')
        fout.write('PRODID:-//Google Inc//Google Calendar 70.9054//EN\n')
        fout.write('VERSION:2.0\n')
        fout.write('CALSCALE:GREGORIAN\n')
        fout.write('METHOD:PUBLISH\n')
        fout.write('X-WR-CALNAME:' + CALENDAR_NAME + '\n')
        fout.write('X-WR-TIMEZONE:Etc/GMT\n')
        fout.write('X-WR-CALDESC:\n')

        line = "bla"
        # Search for the schedule table
        while len(line) > 0 and line.find("<table") != 0:
            line = fin.readline()
        # Skip a few tokens...
        skip_token("<thead>", fin)
        skip_token("<tr", fin)
        # Retrieve the table structure
        line = fin.readline()
        i = 0
        while not line.find("</tr>") == 0:
            try:
                content = td_re.match(line).group(1)
            except Exception as e:
                print_verb('Failed to retrieve content from table cell!')
                print_verb('line: \'{:s}\''.format(line))
                print_verb(str(e))
                print_verb('Exiting...')
                sys.exit(1)
            if content == "Start Time":
                i_start_time = i
            elif content == "Name":
                i_name = i
            elif content == "Runners":
                i_runners = i
            elif content == "Run Time":
                i_run_time = i
            elif content == "Category":
                i_category = i
            elif content == "Setup Time":
                i_setup_time = i
            elif content == "Description":
                i_description = i
            else:
                print_verb('Unkown table header: \'{:s}\''.format(content))
                print_verb('Exiting...')
                sys.exit(1)
            i += 1
            line = fin.readline()
        # Skip a few tokens...
        skip_token("</thead>", fin)
        skip_token("<tbody", fin)
        # Retrieve the table contents
        line = fin.readline()
        uid = 0
        while not line.find("</tbody>") == 0:
            if line.find("<tr") == 0:
                i = 0
                ev = {}
            elif line.find("</tr>") == 0:
                if ev['name'].find("Finale!") == 0:
                    # Complete the final event so no exceptions are thrown
                    ev['run time'] = "00:00:00"
                    ev['setup time'] = "00:00:00"

                # Retrieve the event time
                try:
                    dt_start = dt.datetime.strptime(ev['start'], '%Y-%m-%dT%H:%M:%SZ')
                    dt_delta = dt.datetime.strptime(ev['run time'], '%H:%M:%S')
                    dt_setup = dt.datetime.strptime(ev['setup time'], '%H:%M:%S')
                except Exception as e:
                    print_verb('Got error on event: \'{:s}\''.format(str(ev)))
                    print_verb(str(e))
                    print_verb('Exiting...')
                    sys.exit(1)

                dt_end = dt_start + dt.timedelta(hours=dt_delta.hour, minutes=dt_delta.minute, seconds=dt_delta.second)
                dt_end = dt_end + dt.timedelta(hours=dt_setup.hour, minutes=dt_setup.minute, seconds=dt_setup.second)

                # Separate each field
                Subject = ev['name']
                StartDate = '{:02d}{:02d}{:02d}T{:02d}{:02d}{:02d}Z'.format(
                                                                            dt_start.year,
                                                                            dt_start.month,
                                                                            dt_start.day,
                                                                            dt_start.hour,
                                                                            dt_start.minute,
                                                                            dt_start.second)
                EndDate = '{:02d}{:02d}{:02d}T{:02d}{:02d}{:02d}Z'.format(
                                                                          dt_end.year,
                                                                          dt_end.month,
                                                                          dt_end.day,
                                                                          dt_end.hour,
                                                                          dt_end.minute,
                                                                          dt_end.second)
                AllDayEvent = "False"
                Private = "False"
                Description = ''
                if 'runners' in ev and len(ev['runners']) > 0:
                    Description += 'Runners: {}\\n'.format(ev['runners'])
                if 'cat' in ev and len(ev['cat']) > 0:
                    Description += 'Category: {}\\n'.format(ev['cat'])
                if 'run time' in ev and len(ev['run time']) > 0:
                    if dt_end >= dt_now:
                        Description += 'Estimate: {:02d}:{:02d}:{:02d}\\n'.format(dt_delta.hour,
                                                                                  dt_delta.minute,
                                                                                  dt_delta.second)
                    else:
                        Description += 'Run time: {:02d}:{:02d}:{:02d}\\n'.format(dt_delta.hour,
                                                                                  dt_delta.minute,
                                                                                  dt_delta.second)
                if 'setup time' in ev and len(ev['setup time']) > 0:
                    Description += 'Setup: {:02d}:{:02d}:{:02d}\\n'.format(dt_setup.hour, dt_setup.minute, dt_setup.second)
                if 'desc' in ev and len(ev['desc']) > 0:
                    Description += 'Others: {}'.format(ev['desc'])

                # Output it all to the csv
                fout.write('BEGIN:VEVENT\n');
                fout.write('DTSTART:{}\n'.format(StartDate));
                fout.write('DTEND:{}\n'.format(EndDate));
                fout.write('UID:AGDQ2016CALBYGFM{}\n'.format(uid));
                fout.write('DESCRIPTION:{}\n'.format(Description));
                fout.write('LOCATION:\n');
                fout.write('SEQUENCE:{}\n'.format(UPDATE_VERSION))
                fout.write('STATUS:CONFIRMED\n');
                fout.write('SUMMARY:{}\n'.format(Subject));
                fout.write('TRANSP:OPAQUE\n');
                fout.write('END:VEVENT\n');
                uid += 1
            else:
                content = td_re.match(line).group(1)
                if i == i_start_time:
                    ev['start'] = content
                elif i == i_name:
                    ev['name'] = content
                elif i == i_runners:
                    ev['runners'] = content
                elif i == i_run_time:
                    ev['run time'] = content
                elif i == i_category:
                    ev['cat'] = content
                elif i == i_setup_time:
                    ev['setup time'] = content
                elif i == i_description:
                    ev['desc'] = content
                else:
                    print_verb('Something strange happened on line \'{:s}\''.format(line))
                i += 1
            line = fin.readline()
        fout.write('END:VCALENDAR\n');

print_verb('iCal generated successfully!')

# Delete the temporary file
print_verb('Removing downloaded file...')
os.remove(TEMP_FILE)

# Write the hash now that the calendar was generated
print_verb('Storing hash of the downloaded file...')
with open(HASH_FILE, 'wt') as fout:
    fout.write(str_hash)

# Update the calendar version
print_verb('Storing version of the current calendar')
with open(VERSION_FILE, "wt") as fout:
    fout.write('{:d}'.format(UPDATE_VERSION))

os.system('notify-send -u LOW -t 1500 "{:s} calendar updated"'.format(CALENDAR_NAME))

