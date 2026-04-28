from cm2.circuitry.hdl import json_to_module
import sys
import os

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <json_file> <entry_module> [output]", file = sys.stderr)
    sys.exit(1)

json_file = sys.argv[1]
entry_module = sys.argv[2]
output = "build.txt"
if len(sys.argv) >= 4:
    output = sys.argv[3]

assert os.path.exists(json_file), f"Json file '{json_file}' doesn't exists"

modules = json_to_module(json_file)

assert entry_module in modules, f"The parsed json file does not contain module '{entry_module}'"

modules[entry_module].save(output)