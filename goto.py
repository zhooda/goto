#!/usr/bin/env python3

import os
import signal
import sys
import json


config_path = os.path.join(os.path.expanduser("~"), ".config/goto/workspaces.json")
os.makedirs(os.path.dirname(config_path), exist_ok=True)
# if not os.path.isdir(os.path.dirname(config_path)):


if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        json.dump({"projects": {}}, f)

with open(config_path, "r") as f:
    config = json.load(f)

if len(sys.argv) == 1:
    print(
        (
            f"Usage: \n"
            f"\t{sys.argv[0]} <PROJECT_NAME>\n"
            f"\t{sys.argv[0]} -r <PROJECT_NAME> <PROJECT_PATH>\n"
            f"\t{sys.argv[0]} -d <PROJECT_NAME>\n"
        )
    )
    exit(-1)

if len(sys.argv) == 2:
    if sys.argv[1] not in config["projects"]:
        print(f"Error: {sys.argv[1]} not found in configuration")
        exit(-1)
    if not os.path.exists(config["projects"][sys.argv[1]]):
        print(f"Error: path to {sys.argv[1]} not found")
        exit(-1)
    pid = os.getppid()
    os.chdir(config["projects"][sys.argv[1]])
    os.system("$SHELL")
    os.kill(pid, signal.SIGKILL)

if len(sys.argv) == 3:
    print("Error: deleting projects is unsupported, please edit the configuration file")

if len(sys.argv) == 4:
    project = sys.argv[2]
    path = sys.argv[3]

    config["projects"][project] = path

    with open(config_path, "w") as f:
        json.dump(config, f)
