"""cm2/modules/stdm.py

The standard modules
"""

from cm2.circuitry.core import *
from cm2.utils import closest_divisors

def Adder(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    """
    Creates a Carry Lookahead Adder with Carry
    """
    a = Module(name)
    a.set_size(size)
    a.set_ports({
        "input": ["input.0", "input.1", "input.2"],
        "output": ["output.0", "output.1"]
    })

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

def FullAdder(name: str, pos: Tuple[float, float, float] = (0, 0, 0)):
    a = Module(name)
    a.set_ports({
        "input": ["input.0", "input.1", "input.2"],
        "output": ["output", "carry"]
    })

    a.add([
        Block("input.0", "node", (0, 0, 0)),
        Block("input.1", "node", (1, 0, 0)),
        Block("input.2", "node", (2, 0, 0)),

        Block("xor.0", "xor", (0, 0, -1)),
        Block("and.0", "and", (1, 0, -1)),
        Block("input.2.delay", "delay", (2, 0, -1), properties=["1"]),
        Block("xor.1", "xor", (0, 0, -2)),
        Block("and.1", "and", (1, 0, -2)),
        Block("and.0.delay", "delay", (2, 0, -2), properties=["1"]),

        Block("output", "node", (1, 0, -3)),
        Block("carry", "node", (0, 0, -3)),

        Wire("input.0", "xor.0"),
        Wire("input.0", "and.0"),
        Wire("input.1", "xor.0"),
        Wire("input.1", "and.0"),
        Wire("input.2", "input.2.delay"),
        Wire("input.2.delay", "xor.1"),
        Wire("input.2.delay", "and.1"),

        Wire("xor.0", "xor.1"),
        Wire("xor.0", "and.1"),
        Wire("and.0", "and.0.delay"),
        Wire("and.0.delay", "carry"),

        Wire("xor.1", "output"),
        Wire("and.1", "carry")
    ])
    
    a.move(pos)
    return a

def HalfAdder(name: str, pos: Tuple[float, float, float] = (0, 0, 0)):
    a = Module(name)
    a.set_ports({
        "input": ["input.0", "input.1"],
        "output": ["output", "carry"]
    })

    a.add([
        Block("input.0", "node", (0, 0, 0)),
        Block("input.1", "node", (1, 0, 0)),

        Block("xor", "xor", (0, 0, -1)),
        Block("and", "and", (1, 0, -1)),

        Block("output", "node", (1, 0, -2)),
        Block("carry", "node", (0, 0, -2)),

        Wire("input.0", "xor"),
        Wire("input.0", "and"),
        Wire("input.1", "xor"),
        Wire("input.1", "and"),
        Wire("xor", "output"),
        Wire("and", "carry"),
    ])
    
    a.move(pos)
    return a

def DFF(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    ff = Module(name)
    ff.set_size(size)
    ff.set_ports({
        "input": ["input", "write"],
        "output": ["output"]
    })

    ff.add([
        Array("input", "delay", (0, 0, 0), properties=["2"]),
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
    dc.set_ports({
        "input": ["input"],
        "output": ["output"]
    })

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
    mux.set_ports({
        "input": ["decoder.input"],
        "output": ["output"]
    })

    num_gates = int(2 ** addr_size)

    for i in range(num_gates):
        mux.ports["input"].append(f"input.{i}")

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
    input_array = cast(Array, mux.blocks.get(f"decoder.input"))
    nor_array = cast(Array, mux.blocks.get(f"decoder.nor_gate"))
    or_array = cast(Array, mux.blocks.get(f"decoder.or_gate"))
    input_array.set_pos((data_size + 1, 0, 1))
    nor_array.set_pos((data_size, 0, 1))
    nor_array.set_info(ArrayInfo(x_step=0))
    or_array.set_pos((data_size, 0, 1))
    or_array.set_info(ArrayInfo(x_step=0))
    for i in range(num_gates):
        decoder_block = cast(Block, mux.blocks.get(f"decoder.output.{i}"))
        decoder_block.set_pos((data_size, 0, -i))

    mux.move(pos)
    return mux

def RingCounter(name: str, size: int, pos: Tuple[float, float, float] = (0, 0, 0)):
    r = Module(name)
    r.set_ports({
        "input": ["increment", "decrement"]
    })

    r.add([
        Block("increment", "node", (0, 0, -1)),
        Block("decrement", "node", (0, 0, 0)),

        Block("not_inc", "nor", (1, 0, -1)),
        Block("not_dec", "nor", (1, 0, 0)),
        Wire("increment", "not_inc"),
        Wire("decrement", "not_dec"),

        Block("yes_inc", "or", (2, 0, -1)),
        Block("yes_dec", "or", (2, 0, 0)),
        Wire("increment", "yes_inc"),
        Wire("decrement", "yes_dec"),

        Block("yes_inc_not_dec", "and", (3, 0, -1)),
        Block("yes_dec_not_inc", "and", (3, 0, 0)),
        Wire("yes_inc", "yes_inc_not_dec"),
        Wire("not_dec", "yes_inc_not_dec"),
        Wire("yes_dec", "yes_dec_not_inc"),
        Wire("not_inc", "yes_dec_not_inc"),

        Block("clear", "nor", (4, 0, -1), state=True),
        Wire("yes_inc_not_dec", "clear"),
        Wire("yes_dec_not_inc", "clear"),

        Block("delay_inc", "or", (4, 1, -1)),
        Wire("yes_inc_not_dec", "delay_inc"),

        Block("delay_dec", "or", (4, 0, 0)),
        Wire("yes_dec_not_inc", "delay_dec")
    ])

    for i in range(size):
        r.add([
            Block(f"inc_action.{i}", "and", (5 + i, 1, -1)),
            Wire(f"node.{i}", f"inc_action.{i}"),
            Wire("delay_inc", f"inc_action.{i}"),

            Block(f"dec_action.{i}", "and", (5 + i, 0, 0)),
            Wire(f"node.{i}", f"dec_action.{i}"),
            Wire("delay_dec", f"dec_action.{i}"),   

            Wire(f"trap.{i}", f"node.{i}"),
            Wire(f"node.{i}", f"trap.{i}"),
            Wire("clear", f"trap.{i}")
        ])
        
        if size == 1:
            r.add([
                Block(f"node.{i}", "node", (5 + i, 0, -2), state=True),
                Block(f"trap.{i}", "and", (5 + i, 0, -1), state=True),

                Wire(f"inc_action.{i}", f"node.{i}"),
                Wire(f"dec_action.{i}", f"node.{i}"),
            ])
        elif i == size - 1:
            r.add([
                Block(f"node.{i}", "node", (5 + i, 0, -2)),
                Block(f"trap.{i}", "and", (5 + i, 0, -1)),

                Wire(f"inc_action.{i}", f"node.{i}"),
                Wire(f"dec_action.{i}", f"node.{i - 1}"),  
            ])
        elif i == 0:
            r.add([
                Block(f"node.{i}", "node", (5 + i, 0, -2), state=True),
                Block(f"trap.{i}", "and", (5 + i, 0, -1), state=True),

                Wire(f"inc_action.{i}", f"node.{i + 1}"),
                Wire(f"dec_action.{i}", f"node.{i}"),
            ])
        else:
            r.add([
                Block(f"node.{i}", "node", (5 + i, 0, -2)),
                Block(f"trap.{i}", "and", (5 + i, 0, -1)),

                Wire(f"inc_action.{i}", f"node.{i + 1}"),
                Wire(f"dec_action.{i}", f"node.{i - 1}"),
            ])

    r.move(pos)
    return r