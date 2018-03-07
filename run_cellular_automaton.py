#!/usr/bin/python3

# import event class
import event_model as em
import json
import validator_lite as vl
import os

from CellularAutomaton.CellularAutomaton import CellularAutomaton
from classical_solver import classical_solver
from graph_dfs import graph_dfs

solutions = {}



# For 1 of the files; algorithm runs quickly
f = open("velojson/9.json")
json_data = json.loads(f.read())
event = em.event(json_data)
f.close()

# solve with CA
ca = CellularAutomaton()
solutions["CA"] = ca.solve(event)

for k, v in iter(sorted(solutions.items())):
    print("%s method validation" % (k))
    vl.validate_print([json_data], [v])
    print()





# For all 30 Jsons

# for file in os.listdir("velojson"):
#
#     if file.endswith(".json"):
#
#                 print(file)
#         f = open("velojson/"+file)
#
#         json_data = json.loads(f.read())
#         event = em.event(json_data)
#         f.close()
#
#         # Solve with the classic method
#         classical = classical_solver()
#         solutions["classic"] = classical.solve(event)
#
#         # Solve with the DFS method
#         dfs = graph_dfs()
#         solutions["dfs"] = dfs.solve(event)
#
#         solve with CA
#         ca = CellularAutomaton()
#         solutions["CA"] = ca.solve(event)
#
#         for k, v in iter(sorted(solutions.items())):
#             print("%s method validation" % (k))
#             vl.validate_print([json_data], [v])
#             print()