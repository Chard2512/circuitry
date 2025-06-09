from cm2.circuitry import *
from cm2.utils import closest_divisors

def Adder(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    """
    Creates a Carry Lookahead Adder with Carry
    """
    a = Module(name)
    a.set_size(size)

    a.add([
        Array("input.0", "node", (0, 0, 0)),
        Array("input.1", "node", (size + 1, 0, 0)),
        Block("input.2", "node", (2*size + 2, 0, 0)),

        Array("generate", "and", (0, 0, -1)),
        Array("propagate", "xor", (size + 1, 0, -1)),
        Block("carry_in", "xor", (2*size + 2, 0, -1)),

        [ Array(f"precarry.{i + 1}", "and", (0, 0, -2), (size + 1) - i)
          for i in range(size + 1) ],
        
        Array("carry", "node", (0, 0, -3), size + 1),
        Array("delay", "delay", (size + 1, 0, -3), properties=["1"]),

        Block("carry_out", "xor", (0, 0, -4)),
        Array("result", "xor", (2, 0, -4)),

        Block("output.0", "node", (0, 0, -5)),
        Array("output.1", "node", (2, 0, -5)),

        Wire("input.2", "carry_in"),
        Wire("carry", "result"),
        Wire("propagate", "delay"),
        Wire("delay", "result"),
        Wire(f"carry.{size}", "carry_out"),
        Wire("carry_out", "output.0"),

        # Inverted
        Wire("input.0", "propagate", True),
        Wire("input.0", "generate", True),
        Wire("input.1", "generate", True),
        Wire("input.1", "propagate", True),
        Wire("result", "output.1", True)
    ])
    for i in range(size):
        a.add([
            Wire(f"generate.{j}", f"precarry.{i + 1}.{j + 1}")
            for j in range(size - i)
        ])
        for j in range(i):
            a.add([
                Wire(f"propagate.{k + j + 1}", f"precarry.{i + 1}.{k + 1}")
                for k in range(size - i)
            ])
    for i in range(size + 1):
        a.add(Wire("carry_in", f"precarry.{i + 1}.0"))
        for j in range(i):
            a.add(Wire(f"propagate.{j}", f"precarry.{i + 1}.0"))
    for i in range(size + 1):
        a.add([
            Wire(f"precarry.{i + 1}.{j}", f"carry.{j + i}")
            for j in range((size + 1) - i)
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
        Array("input", "node", (0, 0, 0)),
        Array("nor_gate", "nor", (0, 0, -1)),
        Array("or_gate", "or", (0, 0, -2)),
        Wire("input", "nor_gate"),
        Wire("input", "or_gate")
    ])

    for i in range(noutputs):
        bin_i = f"{i:0{size}b}"
        
        x = int(bin_i[:x_input_size], 2)
        y = - y_size + (int(bin_i[x_input_size:], 2) + 1)
        dc.add(Block(f"output.{i}", "and", (x - (x_size - size) // 2, 0, -3 + y)))
        for b in range(len(bin_i)):
            if bin_i[b] == "1":
                dc.add(Wire(f"or_gate.{b}", f"output.{i}"))
            else:
                dc.add(Wire(f"nor_gate.{b}", f"output.{i}"))

    dc.move(pos)
    return dc

def Mux(name: str, data_size: int, addr_size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    mux = Module(name)
    mux.set_size(data_size)

    num_gates = int(2 ** addr_size)

    mux.add([
        Array(f"output", "node", (0, 0, -num_gates - 1)),
        Decoder("decoder", addr_size),
        [[
            Array(f"input.{i}", "node", (0, 0, -i)),
            Array(f"gate.{i}", "and", (0, 0, -num_gates)),
            Block(f"activate.{i}", "node", (data_size, 0, -num_gates)),
            Wire(f"decoder.output.{i}", f"activate.{i}"),
            Wire(f"input.{i}", f"gate.{i}"),
            Wire(f"activate.{i}", f"gate.{i}"),
            Wire(f"gate.{i}", "output"),
        ] for i in range(num_gates) ]
    ])
    # Decoder repositioning
    input_array: Array = mux.blocks.get(f"decoder.input")
    nor_array: Array = mux.blocks.get(f"decoder.nor_gate")
    or_array: Array = mux.blocks.get(f"decoder.or_gate")
    input_array.set_pos((data_size + 1, 0, 1))
    nor_array.set_pos((data_size, 0, 1))
    nor_array.set_info(ArrayInfo(x_step=0))
    or_array.set_pos((data_size, 0, 1))
    or_array.set_info(ArrayInfo(x_step=0))
    for i in range(num_gates):
        decoder_block: Block = mux.blocks.get(f"decoder.output.{i}")
        decoder_block.set_pos((data_size, 0, -i))

    mux.move(pos)
    return mux

