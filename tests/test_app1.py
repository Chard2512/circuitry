from src.cm2.circuitry import *

m = Module("main")

def test_add_block():
    m.add([
        Block("input", "node", (0, 0, 0))
    ])

    print(m.blocks)

def test_add_array():
    m.add([
        Array("input", 16, "node", (0, 0, 0))
    ])

    print(m.blocks)

def test_connect():
    m.add([
        Block("input", "node", (0, 0, 0)),
        Block("output", "node", (0, 0, -1)),
        Wire("input", "output")
    ])

    m.save("tests/file.txt")

def test_connect_array():
    m.add([
        Block("input", "node", (0, 0, 0)),
        Array("output", 16, "node", (0, 0, -3)),
        Wire("input", "output")
    ])

    m.save("tests/file.txt")

def test_add_building():
    m.add([
        Block("input", "node", (0, 0, -10)),
        Building("mem", "huge_memory", 
            CFrame(
                (0, 0, 0), 
                CFrame.look_at(
                Vector3(0, 0, 0), 
                Vector3(0, 0, 1),
                Vector3(-1, 0, 0)
                ).rot
            )
        )
    ])

    m.save("tests/file.txt")

def test_connect_building():
    m.add([
        Block("input", "node", (0, 0, -10)),
        Building("mem", "huge_memory", 
            CFrame(
                (0, 0, 0)
            )
        ),
        BuildingWire("mem", 0, "IN", "input")
    ])

    m.save("tests/file.txt")

test_connect_building()