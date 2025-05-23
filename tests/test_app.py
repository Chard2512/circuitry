from src.cm2.circuitry import *

main = Module()

input = [main.add_block(Enum.Block.NODE, Vector3(i, 0, 0)) for i in range(16)]
output = [main.add_block(Enum.Block.NODE, Vector3(i, 0, -2)) for i in range(16)]
connections = []

for i in range(16):
    connections.append(main.add_connection(input[i], output[i]))

main.save("tests/file.txt")

