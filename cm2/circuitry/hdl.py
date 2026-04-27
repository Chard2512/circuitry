# hdl.py
# Compiles Hardware Description Language to game's logic
from .builder import *
from cm2.utils import random_id
from cm2.modules.hdlm import *
import json

gate_map: Dict[str, Any] = {
    "$reduce_and": And,
    "$and": And,
    "$_AND_": And,
    "$reduce_or": Or,
    "$or": Or,
    "$_OR_": Or,
    "$reduce_xor": Xor,
    "$xor": Xor,
    "$_XOR_": Xor,
    "$reduce_nand": Nand,
    "$nand": Nand,
    "$_NAND_": Nand,
    "$reduce_nor": Nor,
    "$nor": Nor,
    "$_NOR_": Nor,
    "$_NOT_": Nor,
    "$reduce_xnor": Xnor,
    "$xnor": Xnor,
    "$_XNOR_": Xnor,
    "$_DLATCH_P_": DLatchP,
    "$_DLATCH_N_": DLatchN,
    "$_DFF_P_": DFFP
}

def parse_json_module(name: str, json_module: Dict[str, Any]) -> Module:
    ports = json_module["ports"]
    cells = json_module["cells"]

    components: List[Any] = []
    m = Module(name)
    m.set_ports({
        "input": [],
        "output": []
    })

    def is_bit_on_ports(bit: str):
        if "input" in m.ports and type(m.ports["input"]) == List[str]:
            if bit in m.ports["input"]: return True
        if "output" in m.ports and type(m.ports["output"] == List[str]):
            if bit in m.ports["output"]: return True
        return False
    
    for port in ports.values():
        if port["direction"] == "input":
            p: List[str] = []
            for bit in port["bits"]:
                if isinstance(bit, str):
                    this_id = random_id()
                    components.append(Node(this_id))
                    p.append(this_id)
                else:
                    block_name = f"{bit}"
                    if block_name in p:
                        this_id = random_id()
                        components.append([
                            Node(this_id),
                            Wire(block_name, this_id)
                        ])
                        p.append(this_id)
                    else:
                        components.append(Node(block_name))
                        p.append(block_name)
            m.get_port("input").append(p)
        elif port["direction"] == "output":
            p = []
            for bit in port["bits"]:
                if isinstance(bit, str):
                    this_id = random_id()
                    if bit == "0":
                        components.append(Node(this_id))
                    else:
                        components.append(Flipflop(this_id, state=True))
                    p.append(this_id)
                else:
                    block_name = f"{bit}"
                    if block_name in p or is_bit_on_ports(block_name):
                        this_id = random_id()
                        components.append([
                            Node(this_id),
                            Wire(block_name, this_id)
                        ])
                        p.append(this_id)
                    else:
                        components.append(Node(block_name))
                        p.append(block_name)
            m.ports["output"].append(p)

    for cell_name, cell in cells.items():
        block_name = cell_name
        cell_type = cell["type"]
        
        outputs: List[str] = []
        if "Y" in cell["connections"]:
            outputs = [str(i) for i in cell["connections"]["Y"]]
        elif "Q" in cell["connections"]:
            outputs = [str(i) for i in cell["connections"]["Q"]]

        assert cell_type in gate_map, f"Cell type '{cell_type}' not supported"
        gate_class = gate_map[cell_type]

        if cell_type.startswith("$reduce_"):
            inputs = [str(i) for i in cell["connections"]["A"]]

            if is_bit_on_ports(outputs[0]):
                components.append([
                    [Wire(input, block_name) for input in inputs],
                    gate_class(block_name, outputs[0])
                ])
            else:
                block_name = outputs[0]
                components.append([
                    [Wire(input, block_name) for input in inputs],
                    gate_class(block_name)
                ])
        elif cell_type == "$_NOT_":
            inputs = [str(i) for i in cell["connections"]["A"]]
            for i in range(len(outputs)):
                if is_bit_on_ports(outputs[i]):
                    components.append([
                        Wire(inputs[i], block_name),
                        Wire(inputs[i], block_name),
                        gate_class(block_name, outputs[i])
                    ])
                else:
                    block_name = outputs[i]
                    components.append([
                        Wire(inputs[i], block_name),
                        Wire(inputs[i], block_name),
                        gate_class(block_name)
                    ])
        elif cell_type == "$_DLATCH_P_" or cell_type == "$_DLATCH_N_":
            inputs = [[str(i) for i in cell["connections"]["D"]], [str(i) for i in cell["connections"]["E"]]]
            for i in range(len(outputs)):
                components.append([
                    Wire(inputs[0][i], f"{block_name}.D"),
                    Wire(inputs[1][i], f"{block_name}.E"),
                ])
                if is_bit_on_ports(outputs[i]):
                    components.append([
                        gate_class(block_name),
                        Wire(f"{block_name}.Q", outputs[i])
                    ])
                else:
                    components.append([
                        gate_class(block_name),
                        Node(outputs[i]),
                        Wire(f"{block_name}.Q", outputs[i])
                    ])
        elif cell_type == "$_DFF_P_":
            inputs = [[str(i) for i in cell["connections"]["C"]], [str(i) for i in cell["connections"]["D"]]]
            for i in range(len(outputs)):
                components.append([
                    Wire(inputs[0][i], f"{block_name}.C"),
                    Wire(inputs[1][i], f"{block_name}.D"),
                ])
                if is_bit_on_ports(outputs[i]):
                    components.append([
                        gate_class(block_name),
                        Wire(f"{block_name}.Q", outputs[i])
                    ])
                else:
                    components.append([
                        gate_class(block_name),
                        Node(outputs[i]),
                        Wire(f"{block_name}.Q", outputs[i])
                    ])
        else:
            inputs = [[str(i) for i in cell["connections"]["A"]], [str(i) for i in cell["connections"]["B"]]]
            for i in range(len(outputs)):
                if is_bit_on_ports(outputs[i]):
                    components.append([
                        Wire(inputs[0][i], block_name),
                        Wire(inputs[1][i], block_name),
                        gate_class(block_name, outputs[i])
                    ])
                else:
                    block_name = outputs[i]
                    components.append([
                        Wire(inputs[0][i], block_name),
                        Wire(inputs[1][i], block_name),
                        gate_class(block_name)
                    ])   

    m.add(components)
    m.auto_place()
    return m

def json_to_module(filepath: str) -> Dict[str, Module]:
    """
    Compiles json hdl to Module
    """

    compiled_modules: Dict[str, Module] = {}

    with open(filepath) as file:
        jsonhdl = json.load(file)

    modules = jsonhdl["modules"]

    for module_name, module in modules.items():
        compiled_modules[module_name] = parse_json_module(module_name, module)

    return compiled_modules

def jsons_to_module(filepaths: List[str]) -> Dict[str, Module]:
    """
    Compiles multiple json hdl to Module
    """

    compiled_modules: Dict[str, Module] = {}

    for filepath in filepaths:
        child_compiled_modules = json_to_module(filepath)
        compiled_modules.update(child_compiled_modules)
        
    return compiled_modules