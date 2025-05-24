from src.cm2.circuitry import *

m = Module()

input = m.add_array(16, BlockID.NODE, Vector3(0, 0, 0))
output = m.add_array(16, BlockID.NODE, Vector3(0, 0, -2))
pass_gate = m.add_array(16, BlockID.AND, Vector3(0, 1, -1))
trap_gate = m.add_array(16, BlockID.AND, Vector3(0, 0, -1))
pass_activate = m.add_block(BlockID.OR, Vector3(16, 1, -1))
trap_activate = m.add_block(BlockID.NOR, Vector3(16, 0, -1))
activate = m.add_block(BlockID.NODE, Vector3(16, 0, 0))
m.connect_arrays(input, pass_gate)
m.connect_arrays(pass_gate, output)
m.connect_arrays(trap_gate, output)
m.connect_arrays(output, trap_gate)
m.connect_one_to_many(pass_activate, pass_gate)
m.connect_one_to_many(trap_activate, trap_gate)
m.connect_blocks(activate, pass_activate)
m.connect_blocks(activate, trap_activate)

m.save("tests/file.txt")
