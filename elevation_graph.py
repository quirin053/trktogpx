from asyncio.windows_events import NULL
from cProfile import label
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import math
# https://www.kaggle.com/code/pabloatienza/track-profile-gpx-plotting-python/notebook


class Track():
    

    def distance(self, prev_point: gpxpy.gpx.GPXTrackPoint, point: gpxpy.gpx.GPXTrackPoint):
        d=math.sqrt((prev_point.longitude-point.longitude)**2+(prev_point.latitude-point.latitude)**2)
        return d

    def __init__(self, filename, name):
        self.name = name
        self.lat_list=[]
        self.ele_list=[]
        self.lon_list=[]
        self.d_list=[0.0]
        gpx_file = open(filename, 'r')
        gpx = gpxpy.parse(gpx_file)
        prev_point = NULL
        l = 0
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.lon_list.append(point.longitude)
                    self.lat_list.append(point.latitude)
                    self.ele_list.append(point.elevation)
                    if prev_point:
                        self.d_list.append(self.d_list[-1]+self.distance(prev_point, point))
                    prev_point = point
                    l += 1

tracks = [Track('78.gpx','srtm'),Track('76.gpx','raw gps'),Track('77.gpx','gpxz')]

base_reg = 0

plt.figure(figsize=(8*1.5,5*1.1))
for track in tracks:
    plt.plot(track.d_list,track.ele_list, label=track.name)
plt.ylabel("GPS Elevation(m)")
plt.xlabel("Distance")
plt.grid()
plt.legend()
plt.show()