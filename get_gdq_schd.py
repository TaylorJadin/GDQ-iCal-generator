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
import os
import re
import sys

#== CONST =====================================================================#

CALENDAR_FILE='cal.ical.ics'
CALENDAR_URL='https://gamesdonequick.com/schedule'
CALENDAR_NAME='AGDQ 2016'
TEMP_FILE='/tmp/temp_cal.html'

# TODO Get this somehow
HOME='/home/gfm/'
# TODO Auto increase in a cleaner way
os.system('VERSION=0;'
          'if [ -f ~/gdq_cal_version ];'
              'then VERSION=`cat ~/gdq_cal_version`;'
              'VERSION=$(($VERSION+1));'
          'fi;'
          'echo -n "$VERSION" > ~/gdq_cal_version')
with open(HOME + '/gdq_cal_version') as fin:
    UPDATE_VERSION=fin.readline()

td_re = re.compile(r'<td.*?>(.*?)</td>')

#== HELPER FUNCTIONS ==========================================================#

def skip_token(tk, f):
    line = f.readline()
    if line.find(tk) != 0:
        print line
    assert line.find(tk) == 0

#== MAIN ======================================================================#

# Download the schedule
# TODO Use urllib to get the job done!
os.system("wget -q -O" + TEMP_FILE + " " + CALENDAR_URL)
if not os.path.isfile(TEMP_FILE):
    print "Failed to Download the calendar"
    sys.exit(1)

# Open both input and output files
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
                print "line: '" + line + "'"
                print e
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
                print "Unkown table header: '" + content + "'"
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
                    print "Got error on event: " + str(ev)
                    print e
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
                    Description += 'Estimate: {:02d}:{:02d}:{:02d}\\n'.format(dt_delta.hour, dt_delta.minute, dt_delta.second)
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
                    print "Something strange happened on line '" + line + "'"
                i += 1
            line = fin.readline()
        fout.write('END:VCALENDAR\n');

# Delete the temporary file
os.remove(TEMP_FILE)

