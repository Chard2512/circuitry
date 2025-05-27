from src.cm2.circuitry import *

main = Module("main")

def Flipflop(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    ff = Module(name)

    ff.add([
        Array("input", size, "node", (0, 0, 0)),
        Array("output", size, "node", (0, 0, -2)),
        Array("trap", size, "and", (0, 0, -1)),
        Array("pass", size, "and", (0, 1, -1)),
        Block("act_trap", "nor", (size, 0, -1)),
        Block("act_pass", "or", (size, 1, -1)),
        Block("write", "node", (size, 0, 0)),
        
        Wire("input", "pass"),
        Wire("pass", "output"),
        Wire("trap", "output"),
        Wire("output", "trap"),
        Wire("act_trap", "trap"),
        Wire("act_pass", "pass"),
        Wire("write", "act_trap"),
        Wire("write", "act_pass")
    ])

    ff.move(pos)

    return ff

main.add([
    Flipflop("ff1", 16, (0, 0, 0)),
    Flipflop("ff2", 16, (0, 0, -4)),
    Wire("ff1.output", "ff2.input")
])

main.save("tests/file.txt")