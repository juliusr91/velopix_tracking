
Track reconstruction made easy
==============================

This is a pet project to do track reconstruction,
based on real data coming from the LHCb detector at CERN.

Think you can make it better? Go ahead and try!


```python
from simple_track_forwarding import *
```

What is track reconstruction?
-----------------------------

At the LHCb detector, millions of particles collide at speeds
close to the speed of light, leaving traces (hits) on the sensors
placed in their way.

The collisions that happen at the same time are packed
into an *event*, and sent to one of our servers,
that must reconstruct the tracks that formed each particle
in real time.

This project contains events in json format. These events are
then processed by some reconstruction algorithm, and finally
the results are validated. That is, the particles found by
the solver are matched against the real particles that came out of
the collisions in the event.

![velopix reconstruction example](reco_example.png "velopix reconstruction example")

The algorithm included is just one way of doing it, but perhaps
not the most efficient one!

Diving into details
-------------------

Input files are specified in json. An *event model* to parse them
is shipped with this project.


```python
import event_model as em
import json
f = open("velojson/0.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()
```

The LHCb Velopix detector has 52 sensors. Spread across the sensors,
we should have many hits, depending on the event we are on.


```python
print(len(event.sensors))
print(len(event.hits))
```

    52
    1003


Hits are composed of an ID, and {x, y, z} coordinates.


```python
print(event.hits[0])
```

    #0 {-3.385275, 13.436796, -275.531006}


Sensors are placed at some z in the detector. Each sensor
may have as many hits as particles crossed by it, plus some noise to
make things interesting.


```python
print(event.sensors[0])
```

    Sensor 0:
     At z: -275
     Number of hits: 18
     Hits (#id {x, y, z}): [#0 {-3.385275, 13.436796, -275.531006}, #1 {0.017677, 13.495132, -275.531006}, #2 {0.464924, 12.270069, -275.531006}, #3 {-0.896257, 10.908888, -275.531006}, #4 {1.417747, 13.067333, -275.531006}, #5 {3.828983, 13.37846, -275.531006}, #6 {4.529018, 2.722359, -275.531006}, #7 {7.231934, 0.913937, -275.531006}, #8 {24.997992, 21.066479, -274.468994}, #9 {14.341893, 28.261292, -274.468994}, #10 {-1.207973, 31.742023, -274.468994}, #11 {3.986314, -5.6763, -274.468994}, #12 {13.572914, -10.634886, -274.468994}, #13 {7.894847, -1.534422, -274.468994}, #14 {10.928335, -3.323402, -274.468994}, #15 {30.529337, -0.678823, -275.531006}, #16 {26.154114, -9.526497, -275.531006}, #17 {21.934456, -16.507406, -275.531006}]


A simplistic implementation runs through all sensors sequentially,
finding tracks by matching hits in a straight line.


```python
from classical_solver import classical_solver
tracks = classical_solver().solve(event)
print(len(tracks))
print(tracks[0])
```

    Invoking classic solver with
     max slopes: (0.7, 0.7)
     max tolerance: (0.4, 0.4)
     max scatter: 0.4
    
    117
    Track hits #14: [#984 {5.485382, -22.965059, 736.968994}, #942 {5.115919, -21.623325, 686.968994}, #900 {4.785345, -20.28159, 636.968994}, #856 {4.435328, -18.959301, 586.968994}, #816 {3.754736, -16.295275, 486.968994}, #777 {3.093594, -13.611805, 386.968994}, #739 {2.646347, -11.608925, 311.968994}, #700 {2.315776, -10.267189, 261.968994}, #660 {2.160213, -9.567154, 236.968994}, #604 {2.100107, -9.273705, 225.531006}, #558 {1.944543, -8.573669, 200.531006}, #510 {1.769534, -7.89308, 175.531006}, #467 {1.613971, -7.193043, 150.531006}, #426 {1.438962, -6.512453, 125.530998}]


Finally, we should validate these results, and we'll look
at three things:
    
*   Reconstruction Efficiency: The fraction of real particles we have reconstructed.
    > \# correctly reconstructed / \# real tracks

*   Clone Tracks: Tracks that are similar to other correctly reconstructed tracks.
    > \# clone tracks / \# correctly reconstructed

*   Ghost Tracks: Tracks that are incorrect, either created by noise or by incorrectly reconstructing a track.
    > \# incorrectly reconstructed / \# all reconstructed

We will get the validation detailed for different kinds of particles.


```python
import validator_lite as vl
vl.validate_print([json_data], [tracks])
```

    117 tracks including        3 ghosts (  2.6%). Event average   2.6%
                  velo :      107 from      114 ( 93.9%,  93.9%)        2 clones (  1.87%), purity: ( 98.99%,  98.99%),  hitEff: ( 98.01%,  98.01%)
                  long :       39 from       39 (100.0%, 100.0%)        2 clones (  5.13%), purity: ( 97.98%,  97.98%),  hitEff: ( 96.74%,  96.74%)
             long>5GeV :       30 from       30 (100.0%, 100.0%)        2 clones (  6.67%), purity: ( 98.03%,  98.03%),  hitEff: ( 96.45%,  96.45%)
          long_strange :        2 from        2 (100.0%, 100.0%)        0 clones (  0.00%), purity: (100.00%, 100.00%),  hitEff: (100.00%, 100.00%)
    None
            long_fromb :       13 from       13 (100.0%, 100.0%)        0 clones (  0.00%), purity: ( 98.46%,  98.46%),  hitEff: ( 98.46%,  98.46%)
       long_fromb>5GeV :       12 from       12 (100.0%, 100.0%)        0 clones (  0.00%), purity: (100.00%, 100.00%),  hitEff: (100.00%, 100.00%)


# Visualize

The below visualisation is built on plotly and only does a very basic visualisation of the particles, tracks and sensors in an interactive 3D graph. It can also generate HTML files of the same graph. 


```python
from utils.visualizer import visualizer
import plotly
plotly.offline.init_notebook_mode()
```

Create a visualizer class and pass to it the hits, sensors and or tracks


```python
vis = visualizer(event.hits, event.sensors)
```

Didnt include all the data in the beginning? Use one of the three setters. 
To view the data you can also use a getter. 


```python
vis.set_tracks(tracks)
```

Use the full graph function to fiew all the data. Using draw_tracks, draw_sensor or draw_particles you can decide the data displayed. Additionally, you can choose if you want to display the graph directly or make an HTML.


```python
vis.full_graph(draw_particles = True, draw_tracks = True, make_html=True, filename = "3D_tracks_html")
```

Only want to see x amount of random tracks? 
Use the draw_random_tracks function. You can pass the number of tracks, use draw_tracks and use make_html.

The camera of the plotly library does not working 100% correct, to view the graph in standard CERN format click the camera in the upper right corner of the graph ("Reset camera to last save"). That sets the view to the standard visualisation. 


```python
vis.draw_random_tracks(20, filename = "random_3D_tracks_html")
```


<div id="53764cc8-314d-4c16-b2a2-e782a2043b10" style="height: 525px; width: 100%;" class="plotly-graph-div"></div><script type="text/javascript">require(["plotly"], function(Plotly) { window.PLOTLYENV=window.PLOTLYENV || {};window.PLOTLYENV.BASE_URL="https://plot.ly";Plotly.newPlot("53764cc8-314d-4c16-b2a2-e782a2043b10", [{"type": "scatter3d", "x": [14.584078, 11.881162, 9.178246, 6.47533], "y": [-10.323759, -8.398661, -6.473562, -4.587356], "z": [25.531, 0.531, -24.469, -49.469002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [19.55327, 16.675346, 13.797421, 10.771002, 7.912525, 5.034599], "y": [24.21664, 20.63868, 17.099609, 13.397905, 9.83939, 6.261429], "z": [150.531006, 125.530998, 100.530998, 74.469002, 49.469002, 24.469], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-31.307152, -24.831821, -18.375937, -11.607157, -4.723473], "y": [-10.029131, -8.207741, -6.379871, -4.485413, -2.60569], "z": [263.031006, 238.031006, 213.031006, 186.968994, 161.968994], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [9.448713, 8.807014, 7.426388, 6.14299, 5.229055, 4.6068, 4.334564, 4.023438, 3.712311, 3.42063, 3.090057, 2.778928], "y": [13.709032, 12.833988, 11.453362, 9.703274, 8.322645, 7.389263, 6.883686, 6.416996, 5.911411, 5.425274, 4.93914, 4.47245], "z": [649.468994, 599.468994, 499.468994, 399.468994, 324.468994, 274.468994, 249.468994, 224.468994, 199.468994, 174.468994, 149.468994, 124.469002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [31.190483, 28.098656, 25.045727, 21.953899, 19.037083, 15.945258, 12.872879, 9.781055], "y": [-13.396139, -11.937731, -10.44043, -8.982023, -7.543062, -6.084654, -4.567909, -3.109503], "z": [149.468994, 124.469002, 99.469002, 74.469002, 50.530998, 25.531, 0.531, -24.469], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [7.54306, 6.318001, 5.365171, 4.762365, 4.470684, 4.023438], "y": [10.986671, 9.178246, 7.83651, 6.922573, 6.47533, 6.416996], "z": [499.468994, 399.468994, 324.468994, 274.468994, 249.468994, 224.468994], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-10.831108, -13.572918, -16.217495, -18.842628], "y": [11.47104, 14.36841, 17.168554, 19.949251], "z": [-211.968994, -238.031006, -263.031006, -288.031006], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-5.891967, -7.311484, -8.769892, -10.189408], "y": [5.442955, 6.78469, 8.126425, 9.429269], "z": [-211.968994, -236.968994, -261.968994, -286.968994], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-24.365131, -22.984505, -21.545544, -20.126026, -17.228657, -14.331286, -12.153397, -10.656099, -9.917171, -9.1588, -8.419874, -7.700392, -6.922575], "y": [1.126068, 1.067732, 1.028839, 0.970505, 0.834387, 0.73716, 0.698269, 0.665859, 0.678822, 0.659378, 0.659378, 0.639931, 0.639931], "z": [738.031006, 688.031006, 638.031006, 588.031006, 488.031006, 388.031006, 313.031006, 263.031006, 238.031006, 213.031006, 188.031006, 163.031006, 138.031006], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-1.06773, -0.970505, -0.873276, -0.795495], "y": [-8.361538, -7.875401, -7.389267, -6.922573], "z": [736.968994, 686.968994, 636.968994, 586.968994], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-48.263577, -43.81057, -39.357567, -34.924004, -30.471001, -26.193005, -21.68166, -17.13143, -12.56175, -7.972629], "y": [-3.210265, -2.724129, -2.26392, -1.823157, -1.324058, -0.818476, -0.312895, 0.192686, 0.678823, 1.145514], "z": [161.968994, 136.968994, 111.969002, 86.969002, 61.969002, 38.030998, 13.031, -11.969, -36.969002, -61.969002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-44.005024, -38.404739, -32.823898, -27.476402, -21.85667, -16.256384, -10.675544], "y": [-1.362948, -1.207385, -1.019413, -0.857367, -0.682358, -0.500866, -0.312895], "z": [86.969002, 61.969002, 36.969002, 13.031, -11.969, -36.969002, -61.969002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-23.85955, -21.876118, -19.873238, -17.889803, -15.906372, -14.000714, -11.939498, -9.917172, -7.894846, -5.872522], "y": [20.104815, 18.432505, 16.779646, 15.107338, 13.435028, 11.840503, 10.168196, 8.456997, 6.745798, 5.034601], "z": [186.968994, 161.968994, 136.968994, 111.969002, 86.969002, 63.030998, 38.030998, 13.031, -11.969, -36.969002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [9.448713, 8.807014, 7.426388, 6.14299, 5.229055, 4.6068, 4.334564, 4.023438, 3.712311, 3.42063, 3.090057, 2.778928], "y": [13.709032, 12.833988, 11.453362, 9.703274, 8.322645, 7.389263, 6.883686, 6.416996, 5.911411, 5.425274, 4.93914, 4.47245], "z": [649.468994, 599.468994, 499.468994, 399.468994, 324.468994, 274.468994, 249.468994, 224.468994, 199.468994, 174.468994, 149.468994, 124.469002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [4.327494, 4.055258, 3.802465, 3.510786, 2.966314, 2.428911, 2.078895, 1.806658, 1.689984, 1.553866, 1.437193, 1.339968, 1.203849, 1.087176, 0.989948, 0.873278, 0.756604], "y": [35.281094, 33.219879, 31.216999, 29.175226, 25.052795, 20.923288, 17.850908, 15.789694, 14.739639, 13.747925, 12.69787, 11.667261, 10.636654, 9.625492, 8.594883, 7.544827, 6.494774], "z": [750.531006, 700.531006, 650.531006, 600.531006, 500.531006, 399.468994, 324.468994, 274.468994, 249.468994, 224.468994, 199.468994, 174.468994, 149.468994, 124.469002, 99.469002, 74.469002, 49.469002], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [14.61413, 18.678226, 22.742321], "y": [14.45503, 18.480236, 22.505442], "z": [-199.468994, -224.468994, -249.468994], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-10.169963, -12.658978, -15.225777, -17.695351], "y": [8.243097, 10.304314, 12.443312, 14.523973], "z": [-211.968994, -236.968994, -263.031006, -288.031006], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [30.101538, 28.195885, 26.251343, 24.248461, 22.284473, 20.33993, 18.473164, 16.489731, 14.545187, 12.600643, 10.656099, 8.672665, 6.68923], "y": [-12.229412, -11.412703, -10.634886, -9.876514, -9.07925, -8.301434, -7.523617, -6.706907, -5.92909, -5.151272, -4.373455, -3.556747, -2.740039], "z": [274.468994, 249.468994, 224.468994, 199.468994, 174.468994, 149.468994, 125.530998, 100.530998, 75.530998, 50.530998, 25.531, 0.531, -24.469], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-43.693897, -37.140785, -32.746117, -30.646008, -28.429226, -26.212448, -23.995668, -21.778889, -19.562107, -17.345329, -15.147995, -12.950661, -10.733881, -8.555992], "y": [-5.252035, -4.532555, -4.026973, -3.793627, -3.521393, -3.249157, -2.976919, -2.704683, -2.432447, -2.160212, -1.86853, -1.576847, -1.304611, -0.993484], "z": [386.968994, 311.968994, 261.968994, 238.031006, 213.031006, 188.031006, 163.031006, 138.031006, 113.030998, 88.030998, 63.030998, 38.030998, 13.031, -11.969], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}, {"type": "scatter3d", "x": [-30.898796, -27.437508, -23.976223, -20.514935, -16.896313, -13.435028, -9.954296, -6.493008], "y": [-18.669388, -16.569279, -14.469172, -12.330173, -10.163483, -8.050411, -5.969746, -3.86964], "z": [113.030998, 88.030998, 63.030998, 38.030998, 11.969, -13.031, -38.030998, -63.030998], "mode": "markers+lines", "marker": {"size": 4, "line": {"width": 0.1}, "opacity": 0.8}}], {"scene": {"camera": {"up": {"x": 0, "y": 1, "z": 0}, "center": {"x": 0, "y": 0, "z": 0}, "eye": {"x": -2, "y": 0.1, "z": 1}}}}, {"showLink": true, "linkText": "Export to plot.ly"})});</script>

