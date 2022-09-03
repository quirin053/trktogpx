import re
from time import time
import pandas as pd
import gpxpy.gpx
import datetime
import math
import argparse
import os
import srtm

# Example of a .trk Trackpoint
# 1988/8/5  4:1:49
# 48,221282
# 12,902967
# 402,5
# 0

# regex
# (?P<date>(?P<year>\d{4})\/(?P<month>\d{1,2})\/(?P<day>\d{1,2})  (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}))\n(?P<latitude>\d*,\d*)\n(?P<longitude>\d*,\d*)\n(?P<altitude>\d*,\d*)\n(?P<speed>\d*(,\d*)?)

# CLI Parser
parser = argparse.ArgumentParser(description="Convert moveiQ .trk file to .gpx")
split = parser.add_mutually_exclusive_group()
elevation = parser.add_mutually_exclusive_group()
parser.add_argument("filename", type=argparse.FileType('r'), help="input file path")
parser.add_argument("--time", "-t", help="actual recording start time")
parser.add_argument("--sync", help="1. GPS Time, 2. Camera Time", nargs=2)
parser.add_argument("--output", "-o", help="Output file Name")
split.add_argument("--dontsplit", help="dont split the track into segments", action="store_true")
split.add_argument("--separate", "-s", help="save track segments to separate files", action="store_true")
parser.add_argument("--maxtime", help="maximum time between trackpoints for splitting, hh-mm")
parser.add_argument("--maxdistance", help="maximum distance between trackpoints for splitting, in degree")
elevation.add_argument("--srtm", help="replace redorded elevation data with srtm data", action="store_true")
# elevation.add_argument("--gpxz", help="replace redorded elevation data with gpxz data", action="store_true")
args = parser.parse_args()

# open file
ifile = args.filename
ifile.seek(4239) #skip unreadable content
text = ifile.read()
ifile.close()

# extract trackpoints
trackpoint_pattern = re.compile(r'(?P<date>(?P<year>\d{4})\/(?P<month>\d{1,2})\/(?P<day>\d{1,2})  (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}))\n(?P<latitude>\d*,\d*)\n(?P<longitude>\d*,\d*)\n(?P<altitude>\d*,\d*)\n(?P<speed>\d*(,\d*)?)')

data = []

for match in trackpoint_pattern.finditer(text):
    # print(match.group(0))
    pointtime = datetime.datetime(int(match.group('year')), int(match.group('month')), int(match.group('day')), int(match.group('hour')), int(match.group('minute')), int(match.group('second')))
    trackpoint = {
        'time': pointtime,
        'latitude': float(match.group('latitude').replace(',','.')),
        'longitude': float(match.group('longitude').replace(',','.')),
        'altitude': float(match.group('altitude').replace(',','.')),
        'speed': float(match.group('speed').replace(',','.'))
    }
    data.append(trackpoint)


timeshift = datetime.timedelta(0)
time_pattern = re.compile(r'(?P<year>\d{4})-(?P<month>[01]?\d)-(?P<day>[0123]?\d)-(?P<hour>[012]?\d)-(?P<minute>[0-5]?\d)(-(?P<second>[0-5]?\d))?')

# calculate timeshift for starting time
if args.time:
    match = re.search(time_pattern, args.time)
    actual_start_time = datetime.datetime(
        int(match.group('year')),
        int(match.group('month')),
        int(match.group('day')),
        int(match.group('hour')),
        int(match.group('minute')),
        int(match.group('second') or '0'))
    timeshift = actual_start_time - data[0]['time']

# add timeshift for camerasync
if args.sync:
    match = re.search(time_pattern, args.sync[0])
    camsync_gps_time = datetime.datetime(
        int(match.group('year')),
        int(match.group('month')),
        int(match.group('day')),
        int(match.group('hour')),
        int(match.group('minute')),
        int(match.group('second') or '0'))

    match = re.search(time_pattern, args.sync[1])
    camsync_camera_time = datetime.datetime(
        int(match.group('year')),
        int(match.group('month')),
        int(match.group('day')),
        int(match.group('hour')),
        int(match.group('minute')),
        int(match.group('second') or '0'))
    timeshift += camsync_camera_time - camsync_gps_time

# elevation correction
# srtm
# set cache directory to script location
if args.srtm:
    elevation_data = srtm.get_data(local_cache_dir=os.path.dirname(__file__))
    for trackpoint in data:
        trackpoint['altitude'] = elevation_data.get_elevation(trackpoint['latitude'], trackpoint['longitude'])


# Create points:
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=1234))
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=1235))
# gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=1236))

# create gpx file
gpx = gpxpy.gpx.GPX()
gpx.creator = "trktogpx -- https://github.com/quirin053/trktogpx using https://github.com/tkrajina/gpxpy"

# create first track
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

max_distance = int(args.maxdistance or "0") or 0.1
mtime = args.maxtime.split("-") if args.maxtime else [0,5]
max_time_delta = datetime.timedelta(hours=int(mtime[0]),minutes=int(mtime[1]))

gpx_segment = gpxpy.gpx.GPXTrackSegment()
prev_tp_time = data[0]['time']
prev_tp_pos = [data[0]['latitude'], data[0]['longitude']]

output_file = (args.output.split(".")[0] if args.output else os.path.splitext(ifile.name)[0])
filecount = 0

for trackpoint in data:
    if (trackpoint['time'] - prev_tp_time > max_time_delta or math.sqrt((trackpoint['latitude']-prev_tp_pos[0])**2+(trackpoint['longitude']-prev_tp_pos[1])**2) > max_distance) and not args.dontsplit:
        if args.separate: # create new file
            gpx_track.segments.append(gpx_segment)
            f = open(output_file+"-"+str(filecount)+".gpx", "w")
            f.write(gpx.to_xml())
            f.close()
            gpx_track = gpxpy.gpx.GPXTrack()
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx.tracks.append(gpx_track)
            filecount+=1
        else: # create new track segment
            gpx_track.segments.append(gpx_segment)
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(trackpoint['latitude'], trackpoint['longitude'], elevation=trackpoint['altitude'], time= trackpoint['time']+timeshift))
    prev_tp_time = trackpoint['time']
    prev_tp_pos = [trackpoint['latitude'], trackpoint['longitude']]

gpx_track.segments.append(gpx_segment)
# You can add routes and waypoints, too...

# write (last) file
f = open(output_file+(("-"+str(filecount)) if filecount else "")+".gpx", "w")
f.write(gpx.to_xml())
f.close()