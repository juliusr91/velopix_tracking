import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as pytoolz

import matplotlib
from matplotlib.patches import Circle
from matplotlib.patches import CirclePolygon
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection

import random
import math


class visualizer:

    def __init__ (self, hits = None, sensors = None, tracks = None):
        self.set_coordinates(hits)
        self.set_sensors(sensors)
        self.set_tracks(tracks)


    # setters and getters for coordinates, sensors and tracks
    def set_coordinates(self, hits):
        if hits:
            self.raw_hits = hits
            self.trace, self.x, self.y, self.z = self.extract_coordinates(hits)
        else:
            self.raw_hits = None
            self.trace, self.x, self.y, self.z = None

    def set_sensors(self, sensors):
        if sensors:
            self.raw_sensors = sensors
            self.sensors = self.make_sensor_coordinates(sensors)
        else:
            self.raw_sensors = None
            self.sensors = None

    def set_tracks(self, tracks):
        if tracks:
            self.raw_tracks = tracks
            self.tracks = self.extract_tracks(tracks)
        else:
            self.raw_tracks = None
            self.tracks = None


    def get_coordinates(self):
        if self.trace is None:
            raise AttributeError("The hits weren't set. Please set the hits using the set_coordiantes function.")
        else:
            return self.trace, self.x, self.y, self.z

    def get_sensors(self):
        if self.sensors is None:
            raise AttributeError("The sensors weren't set. Please set the sensors using the set_sensors function.")
        else:
            return self.sensors

    def get_tracks(self):
        if self.tracks is None:
            raise AttributeError("The tracks weren't set. Please set the tracks using the set_tracks function.")
        else:
            return self.tracks

    #extracts the coordinates from the hits into seperate variiables and makes markers for them all
    def extract_coordinates(self, hits):
        x, y, z = zip(*hits)
        trace = go.Scatter3d(
            x = x,
            y = y,
            z = z,
            mode='markers',
            marker=dict(
                size=4,
                line=dict(
                    width=0.1
                ),
                opacity=0.8
            )
        )

        return trace, x, y, z

    #makes the coordinate and plane for each one of the sensors.
    def make_sensor_coordinates(self, sensors):
        x_max = max(self.x)
        x_min = min(self.x)

        y_max = max(self.y)
        y_min = min(self.y)

        xplane=[x_max, x_min]
        yplane=[y_max, y_min]

        sensor_coordinated = []
        for sensor in sensors:
            sensor_coordinated.append(dict(z=[[sensor.z,sensor.z],[sensor.z,sensor.z]], x=xplane,y=yplane, type='surface', showscale=False, opacity=0.4))

        return sensor_coordinated

    #extract tracks and makes lines
    def extract_tracks(self, tracks):
        lines = []
        for index, track in enumerate(tracks):
            x,y,z = zip(*track.hits)
            line = go.Scatter3d(
                x = x,
                y = y,
                z = z,
                mode='lines'
            )
            lines.append(line)
        return lines

    #renders the full grpah.
    #has settings for particles, sensors and tracks. weather to make an html or not
    def full_graph(self, draw_particles = False, draw_sensors = False, draw_tracks = False, make_html = False, filename = "simple-3d-scatter"):
        'A 3d representation of the passed in data for Jupyter notebooks'

        data = []
        if draw_particles:
            data = data + [self.trace]
        if draw_sensors:
            data = data + self.sensors
        if draw_tracks:
            data = data + self.tracks

        camera = dict( up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0), eye=dict(x=-2, y=0.1, z=1))
        fig = go.Figure(data=data)
        fig['layout'].update(scene=dict(camera=camera))

        if make_html:
            plotly.offline.plot(fig, filename=filename + ".html", validate=False)
        else:
            plotly.offline.iplot(fig, filename=filename, validate=False)


    #draws x random tracks, with the particles belonging to it
    def draw_random_tracks(self, number_random_tracks = 10, draw_sensors = False, make_html = False, filename = "simple-3d-scatter"):
        random_lines = []
        for index in range(0, number_random_tracks):
            x,y,z = zip(*random.choice(self.raw_tracks))
            random_line = go.Scatter3d(
                x = x,
                y = y,
                z = z,
                mode='markers+lines',
                marker=dict(
                    size=4,
                    line=dict(
                        width=0.1
                    ),
                    opacity=0.8
                )
            )
            random_lines.append(random_line)

        if draw_sensors:
            random_lines = random_lines + self.sensors


        camera = dict( up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0), eye=dict(x=-2, y=0.1, z=1))
        fig = go.Figure(data=random_lines)
        fig['layout'].update(scene=dict(camera=camera))
        if make_html:
            plotly.offline.plot(fig, filename=filename  + ".html",validate=False)
        else:
            plotly.offline.iplot(fig, filename=filename,validate=False)

    #make a 2D representation of the particles and sensors
    def sensors_to_circles(self):
        fig, ax = plt.subplots(figsize=(15, 15))

        max_sensor = max(self.raw_sensors, key=lambda x:x.z)
        ax.set_xlim((-max_sensor.z/2, max_sensor.z/2))
        ax.set_ylim((-max_sensor.z/2, max_sensor.z/2))
        circles = []
        for index, sensor in enumerate(self.raw_sensors):
            if (sensor.z >=0):
                circles.append(Circle((0,0),sensor.z/2, fill=False, color='black'))
        sensor_circles = PatchCollection(circles, match_original=True)
        ax.add_collection(sensor_circles)


        self.angles = []
        x_coordinate = []
        y_coordinate = []
        for index, hit in enumerate(self.raw_hits):
            x,y,z = hit
            rad = math.atan2(y,x)
            self.angles.append(math.degrees(rad))

            x_coordinate.append(z/2 * math.cos(rad))
            y_coordinate.append(z/2 * math.sin(rad))

        ax.plot(x_coordinate, y_coordinate, 'ro')

        plt.show()


    #histograms for the angles of each
    def angle_histogram(self, bins = 10):
        if not self.angles:
            self.angles = []
            for index, hit in enumerate(self.raw_hits):
                x,y,z = hit
                rad = math.atan2(y,x)
                self.angles.append(math.degrees(rad))

        fig, ax = plt.subplots()
        ax.hist(self.angles, bins = bins)

        plt.show()


class CaVisualizer:
    def __init__(self, doublets = None, long_tracks = None):
        self.doublets = doublets
        self.long_tracks = long_tracks

    def visualize_segments(self, make_html=True, filename="3d-segments"):
        lines = []
        # print(self.segments[0:2])
        for index, sensor in enumerate(self.doublets):
            for doublets in sensor:
                for doublet in doublets:
                    if doublet.state == 1:
                        width = 1
                    else:
                        width = doublet.state * 2
                    # x,y,z = zip(*track.doublets)
                    if doublet.state > 1:
                        x = [doublet.starting_point.x, doublet.ending_point.x]
                        y = [doublet.starting_point.y, doublet.ending_point.y]
                        z = [doublet.starting_point.z, doublet.ending_point.z]
                        line = go.Scatter3d(
                            x = x,
                            y = y,
                            z = z,
                            mode='lines',
                            line = dict(
                                width=width
                            )
                        )
                        # print(line)
                        lines.append(line)

        # print(lines)

        data = []
        data = data + lines

        camera = dict(up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0), eye=dict(x=-2, y=0.1, z=1))
        fig = go.Figure(data=data)
        fig['layout'].update(scene=dict(camera=camera))

        if make_html:
            plotly.offline.plot(fig, filename=filename + ".html", validate=False)
        else:
            plotly.offline.iplot(fig, filename=filename, validate=False)

    def visualize_found_tracks(self, make_html=True, filename="3d-ca-tracks"):

        lines = []
        # print(self.segments[0:2])
        for index, tracks in enumerate(self.long_tracks):
            sorted_tracks = sorted(tracks, key=lambda x: x.z)
            x, y, z = zip(*sorted_tracks)
            # print(x)
            line = go.Scatter3d(
                x = x,
                y = y,
                z = z,
                mode='lines',
                # line = dict(
                #     width=width
                # )
            )
            lines.append(line)

        data = []
        data = data + lines

        camera = dict(up=dict(x=0, y=1, z=0), center=dict(x=0, y=0, z=0), eye=dict(x=-2, y=0.1, z=1))
        fig = go.Figure(data=data)
        fig['layout'].update(scene=dict(camera=camera))

        if make_html:
            plotly.offline.plot(fig, filename=filename + ".html", validate=False)
        else:
            plotly.offline.iplot(fig, filename=filename, validate=False)
