from src.cm2.circuitry import Module, CircuitBuilder

def create_flipflop(module: Module, label: str, size: int):
    builder = CircuitBuilder(module)

    (builder
        .add("input", "array", (0, 0, 0), "node", size)
        .add("output", "array", (0, 0, -2), "node", size)
        .add("pass_gate", "array", (0, 1, -1), "and", size)
        .add("trap_gate", "array", (0, 0, -1), "and", size)
        .add("pass_act", "block", (size, 1, -1), "or")
        .add("trap_act", "block", (size, 0, -1), "nor")
        .add("activate", "block", (size, 0, 0), "node")
        .connect("input", "pass_gate")
        .connect("pass_gate", "output")
        .connect("trap_gate", "output")
        .connect("output", "trap_gate")
        .connect("pass_act", "pass_gate")
        .connect("trap_act", "trap_gate")
        .connect("activate", "pass_act")
        .connect("activate", "trap_act")
    )

    return builder