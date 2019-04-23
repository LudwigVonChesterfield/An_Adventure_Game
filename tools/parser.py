import os
import sys

path = "../code/"
if len(sys.argv) > 1:
    path = sys.argv[1]

destination = open(path + "source.py", "w")


def parse(fp, destination):
    with open(fp) as f:
        for line in f:
            destination.write(line)


parse(path + "__start.py", destination)

for root, dirs, files in os.walk(path):
    for fp in files:
        if fp == "__start.py" or fp == "__end.py" or fp == "source.py":
            continue
        parse(path + fp, destination)

parse(path + "__end.py", destination)

destination.close()
