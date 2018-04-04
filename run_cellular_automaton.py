#!/usr/bin/python3

# import event class
import event_model as em
import json
import validator_lite as vl
import os

from CellularAutomaton.CellularAutomaton import CellularAutomaton
from classical_solver import classical_solver
from graph_dfs import graph_dfs
import time
import csv
import sys

solutions = {}


# For 1 of the files; algorithm runs quickly
# f = open("velojson/9.json")
# json_data = json.loads(f.read())
# event = em.event(json_data)
# f.close()
#
# # solve with CA
# ca = CellularAutomaton()
# # solutions["CA"], times = ca.solve_without_Profiling(event)
# solutions["CA"], times = ca.solve_with_profiling(event)
#
#
# for k, v in iter(sorted(solutions.items())):
#     print("%s method validation" % (k))
#     vl.validate_print([json_data], [v])
#     print()
#
#
# print (times)


# For all 30 Jsons

all_times = []
index = 1
for file in os.listdir("velojson"):



    if file.endswith(".json"):
        # f = open("velojson/23.json")
        f = open("velojson/"+file)

        json_data = json.loads(f.read())
        event = em.event(json_data)
        f.close()


        for a in range(5):
            # current_run = []
            # Solve with the classic method
            # classical = classical_solver()
            # start = time.clock()
            # solutions["classic"] = classical.solve(event)
            # current_run.append(time.clock() - start)

            # Solve with the DFS method
            # dfs = graph_dfs()
            # start = time.clock()
            # solutions["dfs"] = dfs.solve(event)
            # current_run.append(time.clock() - start)

            # solve with CA
            ca = CellularAutomaton()
            start = time.clock()
            # solutions["CA"], time_parts = ca.solve_with_profiling(event)
            solutions["CA"], time_parts = ca.solve_without_Profiling(event)

            # time_parts.append(time.clock() - start)
            # time_parts.append(event.number_of_hits)
            # time_parts.append(max([(len(i.hits())) for i in event.sensors]))
            # all_times.append(time_parts)

            # for k, v in iter(sorted(solutions.items())):
            #     print("%s method validation" % (k))
            #     vl.validate_print([json_data], [v])
            #     # print()
        print("File " + str(index) + " done", file=sys.stderr)
        index += 1

# with open ("Profiling/DetailedMeasure-030518_5runs_per_file.csv", 'a') as output_file:
#     wr = csv.writer(output_file, delimiter=',', lineterminator='\n')
#     # wr.writerow(['CA', 'Total Hits in Event', 'Maximum number of Hits in a Sensor'])
#     wr.writerow(['Doublet Creation', 'Neighbour search', 'CA', 'Extract Possible Tracks', 'Remove Short', 'Remove Ghost and Clones', 'Full Time', 'Total Hits in Event', 'Maximum number of Hits in a Sensor'])
#     for line in all_times:
#         # wr.writerow([line[0], line[1], line[2]])
#         # wr.writerow([line[0]])
#         wr.writerow([line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8]])
#         print(line)
