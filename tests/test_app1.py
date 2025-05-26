from src.cm2.circuitry import *

def test_add_block():
    m = Module()

    m.add([
        Block("input", "node", (0, 0, 0))
    ])

    print(m.blocks)

def test_add_array():
    m = Module()

    m.add([
        Array("input", 16, "node", (0, 0, 0))
    ])

    print(m.blocks)