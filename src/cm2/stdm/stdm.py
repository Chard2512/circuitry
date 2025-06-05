from cm2.circuitry import *
from cm2.utils import closest_divisors

def Adder(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    """
    Creates a Carry Lookahead Adder
    """
    a = Module(name)
    a.set_size(size)

    a.add([
        Array("input.0", "node", (0, 0, 0)),
        Array("input.1", "node", (size + 1, 0, 0)),
        Array("generate", "and", (0, 0, -2)),
        Array("propagate", "xor", (size + 1, 0, -2)),
        Array("delay", "delay", (size + 1, 0, -6), properties=["1"]),
        Array("carry", "node", (0, 0, -6)),
        Array("result", "xor", (0, 0, -8)),
        Array("output", "node", (0, 0, -10)),
        [
            Array(f"precarry.{i}", "and", (0, i, -4), size - i - 1)
            for i in range(size)
        ],

        Wire("input.0", "generate"),
        Wire("input.0", "propagate"),
        Wire("input.1", "generate"),
        Wire("input.1", "propagate"),
        [ # Precarry generation wiring
            [
                Wire(f"generate.{j + i + 1}", f"precarry.{i}.{j}"),
                Wire(f"precarry.{i}.{j}", f"carry.{j}")
            ]  
            for i in range(size)
            for j in range(size - i - 1)
        ],
        [ # Precarry propagation wiring
            Wire(f"propagate.{k + j + 1}", f"precarry.{i}.{k}")
            for i in range(size)
            for j in range(i)
            for k in range(size - i - 1)
        ],
        Wire("carry", "result"),
        Wire("propagate", "delay"),
        Wire("delay", "result"),
        Wire("result", "output")
    ])

    a.move(pos)
    return a

def Flipflop(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    ff = Module(name)
    ff.set_size(size)

    ff.add([
        Array("input", "node", (0, 0, 0)),
        Array("output", "node", (0, 0, -2)),
        Array("trap", "and", (0, 0, -1)),
        Array("pass", "and", (0, 1, -1)),
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
    dc.set_size(size)

    noutputs = int(2 ** size)
    y_size, x_size = closest_divisors(noutputs)
    x_input_size = int(math.log2(x_size))

    dc.add([
        Array("input", "node", (int(size / 2), 0, 0)),
        Array("nor_gate", "nor", (0, 0, -1)),
        Array("or_gate", "or", (size, 0, -1)),
        Wire("input", "nor_gate"),
        Wire("input", "or_gate")
    ])

    for i in range(noutputs):
        bin_i = f"{i:0{size}b}"
        
        x = int(bin_i[:x_input_size], 2)
        y = - y_size + (int(bin_i[x_input_size:], 2) + 1)
        dc.add(Block(f"output{i}", "and", (x + (2 * size - x_size) // 2, 0, -2 + y)))
        for b in range(len(bin_i)):
            if bin_i[b] == "1":
                dc.add(Wire(f"or_gate.{b}", f"output.{i}"))
            else:
                dc.add(Wire(f"nor_gate.{b}", f"output.{i}"))

    dc.move(pos)
    return dc