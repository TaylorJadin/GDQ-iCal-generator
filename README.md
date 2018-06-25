# GDQ iCal generator

## Generated iCals

[Awesome Games Done Quick (AGDQ) 2016](https://calendar.google.com/calendar/ical/itca1dvmn55c782volr60339ms%40group.calendar.google.com/public/basic.ics)

[Summer Games Done Quick (SGDQ) 2016](https://calendar.google.com/calendar/ical/qosbgk781rj80jl9sk64k2o8uo%40group.calendar.google.com/public/basic.ics)

[Awesome Games Done Quick (AGDQ) 2017](https://calendar.google.com/calendar/ical/i3ljn1vgdgj335uoh4uhe03nd4%40group.calendar.google.com/public/basic.ics)

[Summer Games Done Quick (SGDQ) 2017](https://calendar.google.com/calendar/ical/79scsgto6vqo2bn5b3crlf63lo%40group.calendar.google.com/public/basic.ics)

[Awesome Games Done Quick (AGDQ) 2018](https://calendar.google.com/calendar/ical/i746pclvh45csu1u3ms4hgmgj4%40group.calendar.google.com/public/basic.ics)

[Summer Games Done Quick (SGDQ) 2018](https://calendar.google.com/calendar/ical/jehdqctmgodgq69thth3t1d8cc%40group.calendar.google.com/public/basic.ics)

## About

From the [Games Done Quick](https://gamesdonequick.com/) website:

> Games Done Quick is a series of charity video game marathons. These events
> feature high-level play by speedrunners raising money for charity. Games Done
> Quick has teamed up with several charities in its six-year history, such as
> Doctors Without Borders and the Prevent Cancer Foundation.

They have a great [schedule](https://gamesdonequick.com/schedule) on the site,
which is already converted to the local time of the viewer. Whoever (afaik),
there's no public iCal which may be imported into a smartphone's app calendar.

This is where this iCal generator comes in. It downloads the schedule and parse
it into an iCal file. This file may be later imported into any application that
supports it (e.g., a Google Calendar, which may be synced into a smartphone).

The script 'get_gdq_schd.py' handles downloading the latest schedule, checking
if it was updated and generating the new iCal. Since it's intended to be run on
the background, it then issues an alert to the user. The script targets Linux
only (more specifically, Ubuntu). It uses `wget` to download the schedule and
`notify-send` to issue the alert.

The script 'update_calendar.sh' stays in an infinite loop, trying to update the
schedule every thirty minutes. Its the actual intended way to call the python
script.

