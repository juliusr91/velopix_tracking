
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
vis.draw_random_tracks(20, make_html=True,filename = "random_3D_tracks_html")
```
