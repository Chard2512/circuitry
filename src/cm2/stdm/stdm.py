from src.cm2.circuitry import *
from src.cm2.utils import closest_divisors

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

def Decoder(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    dc = Module(name)

    noutputs = int(2 ** size)
    y_size, x_size = closest_divisors(noutputs)
    x_input_size = int(math.log2(x_size))

    dc.add([
        Array("input", size, "node", (int(size / 2), 0, 0)),
        Array("nor_gate", size, "nor", (0, 0, -1)),
        Array("or_gate", size, "or", (size, 0, -1)),
        Wire("input", "nor_gate"),
        Wire("input", "or_gate")
    ])

    for i in range(noutputs):
        bin_i = f"{i:0{size}b}"
        
        x = int(bin_i[:x_input_size], 2)
        y = - y_size + (int(bin_i[x_input_size:], 2) + 1)
        dc.add([Block(f"output{i}", "and", (x + (2 * size - x_size) // 2, 0, -2 + y))])
        for b in range(len(bin_i)):
            if bin_i[b] == "1":
                dc.add([Wire(f"or_gate{b}", f"output{i}")])
            else:
                dc.add([Wire(f"nor_gate{b}", f"output{i}")])

    dc.move(pos)

    return dc