from src.cm2.circuitry import *

def test_add_block():
    m = Module("main")

    m.add([
        Block("input", "node", (0, 0, 0))
    ])

    print(m.blocks)

def test_add_array():
    m = Module("main")

    m.add([
        Array("input", 16, "node", (0, 0, 0))
    ])

    print(m.blocks)

def test_connect():
    m = Module("main")

    m.add([
        Block("input", "node", (0, 0, 0)),
        Block("output", "node", (0, 0, -1)),
        Wire("input", "output")
    ])

    m.save("tests/file.txt")

def test_connect_array():
    m = Module("main")

    m.add([
        Block("input", "node", (0, 0, 0)),
        Array("output", 16, "node", (0, 0, -3)),
        Wire("input", "output")
    ])

    m.save("tests/file.txt")

test_connect_array()