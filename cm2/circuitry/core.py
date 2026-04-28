"""cm2/circuitry/core.py

Defines all primitive classes for savestring manipulation.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import cast, Any, List, TypedDict, Optional, Tuple, Dict, Union, Literal, TypeAlias
import math
from enum import IntEnum, Enum
from types import MappingProxyType
from cm2.utils import flatten_recursive, random_id

Component: TypeAlias = Union[
    "Block", "Array", "Wire", "Module", "Building", "BuildingWire",
    List["Component"], List["ConstructComponent"], List["ConnectionComponent"],
    List["PrimitiveComponent"]
]

ConstructComponent: TypeAlias = Union[
    "Block", "Array", "Building",
    List["ConstructComponent"]
]

ConnectionComponent: TypeAlias = Union[
    "Wire", "BuildingWire",
    List["ConnectionComponent"]
]

PrimitiveComponent: TypeAlias = Union[
    "Block", "Array", "Wire",
    List["PrimitiveComponent"]
]

Construct: TypeAlias = Union[
    "Block", "Array", "Building"
]

Connection: TypeAlias = Union[
    "Wire", "BuildingWire"
]

Primitive: TypeAlias = Union[
    "Block", "Array", "Wire"
]

RotationOrder: TypeAlias = Literal['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx']

BIG_INT = 2147483647

# Pre-defined block_id definitions
class BlockID(IntEnum):
    NOR = 0
    AND = 1
    OR = 2
    XOR = 3
    BUTTON = 4
    FLIPFLOP = 5
    LED = 6
    SOUND = 7
    CONDUCTOR = 8
    CUSTOM = 9
    NAND = 10
    XNOR = 11
    RANDOM = 12
    TEXT = 13
    TILE = 14
    NODE = 15
    DELAY = 16
    ANTENNA = 17
    CONDUCTOR_V2 = 18
    LED_MIXER = 19

class BuildingData(Enum):
    HUGE_MEMORY = MappingProxyType({
        "name": "HugeMemory", 
        "nwires": 49, 
        "address_index": 0,
        "address_width": 16,
        "output_index": 16,
        "output_width": 16,
        "value_index": 32,
        "value_width": 16,
        "write_index": 48,
        "write_width": 1,
    })

class Port(IntEnum):
    OUT = 0
    IN = 1

@dataclass
class Vector3:
    """Data class to represent position"""
    x: float
    y: float
    z: float

    @staticmethod
    def zeros() -> 'Vector3':
        return Vector3(0, 0, 0)
    
    @staticmethod
    def ones() -> 'Vector3':
        return Vector3(1, 1, 1)

    def normalize(self) -> 'Vector3':
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        return Vector3(self.x / length, self.y / length, self.z / length)
    
    def cross(self, other: 'Vector3') -> 'Vector3':
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def elementwise_min(self, other: 'Vector3') -> 'Vector3':
        return Vector3(
            min(self.x, other.x),
            min(self.y, other.y),
            min(self.z, other.z)
        )

    def elementwise_max(self, other: 'Vector3') -> 'Vector3':
        return Vector3(
            max(self.x, other.x),
            max(self.y, other.y),
            max(self.z, other.z)
        )

    def __add__(self, other: 'Vector3'):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3'):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __truediv__(self, other: float | int):
        return Vector3(self.x / other, self.y / other, self.z / other)
    
    def __mul__(self, other: float | int):
        return Vector3(self.x * other, self.y * other, self.z * other)
    
    def __round__(self, ndigits: int = 0):
        return Vector3(round(self.x, ndigits), round(self.y, ndigits), round(self.z, ndigits))
    
@dataclass
class CFrame:
    pos: Vector3 | Tuple[float, float, float]
    rot: List[List[float]] = field(default_factory=lambda: [[0, 0, -1], [0, 1, 0], [1, 0, 0]])

    def __post_init__(self):
        if isinstance(self.pos, Tuple):
            self.pos = Vector3(*self.pos)

    @staticmethod
    def identity_matrix():
        return [
            [1, 0, 0],  # Right
            [0, 1, 0],  # Up
            [0, 0, 1]   # Backward
        ]

    @staticmethod
    def look_at(from_pos: Vector3, to_pos: Vector3, up: Vector3 = Vector3(0, 1, 0)):
        forward = (to_pos - from_pos).normalize()
        
        if abs(forward.x - up.x) < 1e-6 and abs(forward.y - up.y) < 1e-6 and abs(forward.z - up.z) < 1e-6:
            up = Vector3(0, 0, 1)

        right = up.cross(forward).normalize()
        up = forward.cross(right).normalize()

        rotation = [
            [right.x, right.y, right.z],    # Right
            [up.x, up.y, up.z],             # Up
            [forward.x, forward.y, forward.z]  # Forward (yeah, idk why)
        ]

        return CFrame(from_pos, rotation)

    @staticmethod
    def angles(euler_angles: Tuple[float, float, float], rotation_order: RotationOrder = 'zyx') -> List[List[float]]:
        """
        Create a rotation matrix from euler angles.
        rotation_order defines the rotation apply order.
        """
        roll, pitch, yaw = euler_angles
        roll = np.radians(roll)
        pitch = np.radians(pitch)
        yaw = np.radians(yaw)

        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(roll), -np.sin(roll)],
            [0, np.sin(roll), np.cos(roll)]
        ])

        Ry = np.array([
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])

        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw), np.cos(yaw), 0],
            [0, 0, 1]
        ])

        rotation_map = {
            'x': Rx,
            'y': Ry,
            'z': Rz
        }

        r = np.eye(3)
        for axis in reversed(rotation_order):  # Note: rotations are applied right-to-left
            r = r @ rotation_map[axis]

        # Necessary unnecessary statement, because linter fears this gonna be a bool instead of a list
        R_list = cast(List[List[float]], r.tolist())
        return R_list

    def __repr__(self):
        return f"CFrame(pos={self.pos}, rot={self.rot})"

class Block:
    def __init__(
            self, 
            name: str, 
            block_id: str = "node", 
            pos: Tuple[float, float, float] = (0, 0, 0), 
            state: bool = False, 
            properties: Optional[List[str]] = None
    ):
        self.name = name
        self.block_id = block_id
        self.state = state
        self.pos = Vector3(*pos) if pos else Vector3(0, 0, 0)
        self.properties = properties

    def set_pos(self, pos: Tuple[float, float, float]):
        self.pos = Vector3(*pos)

    def savestring_encode(self):
        savestring_table = [
            str(BlockID[str.upper(self.block_id)]),
            ("1" if self.state else "0"),
            str(round(self.pos.x, 3)),
            str(round(self.pos.y, 3)),
            str(round(self.pos.z, 3)),
            ("" if not self.properties else "+".join(self.properties))
        ]
        return ",".join(savestring_table)
    
    def __repr__(self):
        return (
            f"Block("
            f"block_id={str.upper(self.block_id)},"
            f"state={self.state},"
            f"pos={self.pos},"
            f"properties={self.properties}"
            f")"
        )

class Array:
    def __init__(
        self, 
        name: str, 
        block_id: str = "node",
        pos: Tuple[float, float, float] = (0, 0, 0),
        width: Optional[int] = None, 
        info: Optional["ArrayInfo"] = None,
        state: bool = False, 
        properties: Optional[List[str]] = None
    ):
        self.name = name
        self.width = width 
        self.block_id = block_id
        self.pos = Vector3(*pos) if pos else Vector3(0, 0, 0)
        self.state = state
        self.properties = properties
        default_info: ArrayInfo = {
                "snap_to_grid": True,
                "x_step": 1,
                "y_step": 0,
                "z_step": 0,
                "x_cycle": BIG_INT,
                "y_cycle": BIG_INT,
                "z_cycle": BIG_INT,
                "x_cluster": BIG_INT,
                "y_cluster": BIG_INT,
                "z_cluster": BIG_INT,
                "x_cluster_space": 1,
                "y_cluster_space": 1,
                "z_cluster_space": 1
            }
        if info is not None:
            default_info.update(info)
        self.info = default_info

    def get_blocks(self) -> Dict[str, Block]:
        blocks: Dict[str, Block] = {}
        info = self.info
        assert self.width, "The size of the array must be defined"
        for i in range(self.width):
            x_pos = (info["x_step"] * i + info["x_cluster_space"] * (i // info["x_cluster"]))
            y_pos = (info["y_step"] * i + info["y_cluster_space"] * (i // info["y_cluster"]))
            z_pos = (info["z_step"] * i + info["z_cluster_space"] * (i // info["z_cluster"]))
            x_cycled = (abs(x_pos) % info["x_cycle"]) * np.sign(x_pos)
            y_cycled = (abs(y_pos) % info["y_cycle"]) * np.sign(y_pos)
            z_cycled = (abs(z_pos) % info["z_cycle"]) * np.sign(z_pos)
            pos_offset = Vector3(
                x_cycled,
                y_cycled,
                z_cycled,
            )
            block_pos = self.pos + pos_offset
            blocks[f"{self.name}.{i}"] = Block(
                f"{self.name}.{i}",
                self.block_id,
                (block_pos.x, block_pos.y, block_pos.z),
                self.state,
                self.properties
            )
        
        return blocks

    def set_pos(self, pos: Tuple[float, float, float]):
        self.pos = Vector3(*pos)

    def set_info(self, info: 'ArrayInfo'):
        default_info: ArrayInfo = {
                "snap_to_grid": True,
                "x_step": 1,
                "y_step": 0,
                "z_step": 0,
                "x_cycle": BIG_INT,
                "y_cycle": BIG_INT,
                "z_cycle": BIG_INT,
                "x_cluster": BIG_INT,
                "y_cluster": BIG_INT,
                "z_cluster": BIG_INT,
                "x_cluster_space": 1,
                "y_cluster_space": 1,
                "z_cluster_space": 1
            }
        default_info.update(info)
        self.info = default_info

    def __repr__(self):
        return (
            f"Array("
            f"width={self.width},"
            f"block_id={str.upper(self.block_id)},"
            f"state={self.state},"
            f"pos={self.pos},"
            f"properties={self.properties}"
            f")"
        )

class Wire:
    def __init__(self, src: str, dst: str, inverted: bool = False):
        self.src = src
        self.dst = dst
        self.inverted = inverted

    def savestring_encode(self, block_indexes: Dict[str, int]) -> str:
        assert self.src in block_indexes, f"Source component '{self.src}' not found"
        assert self.dst in block_indexes, f"Destination component '{self.dst}' not found"
        return f"{block_indexes[self.src]},{block_indexes[self.dst]}"
    
    def __repr__(self):
        return f"Wire(src={self.src},dst={self.dst})"

class ArrayInfo(TypedDict, total=False):
    snap_to_grid: bool
    x_step: float
    y_step: float
    z_step: float
    x_cycle: int
    y_cycle: int
    z_cycle: int
    x_cluster: int
    y_cluster: int
    z_cluster: int
    x_cluster_space: float
    y_cluster_space: float
    z_cluster_space: float

class Building():
    def __init__(
        self, 
        name: str, 
        building_type: str, 
        pos: Tuple[float, float, float], # Not implemented
        cframe: CFrame | Tuple[float, float, float],
        nwires: int = 0
    ):
        if isinstance(cframe, Tuple):
            cframe = CFrame(cframe)
        self.name = name
        self.pos = Vector3(*pos)
        self.building_type = building_type
        self.cframe: CFrame = cframe
        if str.upper(self.building_type) in BuildingData.__members__:
            nwires = int(BuildingData[str.upper(self.building_type)].value["nwires"])
        self.wires: List[List[BuildingWire]] = [[] for _ in range(nwires)]

    def set_pos(self, pos: Tuple[float, float, float]):
        self.pos = Vector3(*pos)

    def add_wire(self, building_wire: 'BuildingWire'):
        if isinstance(building_wire.index, str):
            index = int(BuildingData[str.upper(self.building_type)].value[f"{building_wire.index}_index"])
            width = int(BuildingData[str.upper(self.building_type)].value[f"{building_wire.index}_width"])

            arrange = [str(i) for i in range(1, width + 1, 1)]
            arrange = sorted(arrange)
            j = 0
            for i in arrange:
                self.wires[index + j].append(
                    BuildingWire(
                        building_wire.building, 
                        index + j,
                        building_wire.port,
                        f"{building_wire.src}{int(i) - 1}"
                    )
                )
                j += 1
        else:
            index = building_wire.index

            self.wires[index].append(building_wire)

    def savestring_encode(self, block_indexes: Dict[str, int]) -> str:
        assert isinstance(self.cframe.pos, Vector3)

        if str.upper(self.building_type) not in BuildingData.__members__:
            building_type = self.building_type
        else:
            building_type = str(BuildingData[str.upper(self.building_type)].value["name"])

        savestring_table = [
            building_type,
            str(round(self.cframe.pos.x, 3)),
            str(round(self.cframe.pos.y, 3)),
            str(round(self.cframe.pos.z, 3)),
            str(round(self.cframe.rot[0][0], 3)),
            str(round(self.cframe.rot[0][1], 3)),
            str(round(self.cframe.rot[0][2], 3)),
            str(round(self.cframe.rot[1][0], 3)),
            str(round(self.cframe.rot[1][1], 3)),
            str(round(self.cframe.rot[1][2], 3)),
            str(round(self.cframe.rot[2][0], 3)),
            str(round(self.cframe.rot[2][1], 3)),
            str(round(self.cframe.rot[2][2], 3)), 
        ]

        for w in self.wires:
            if w == []: # Empty
                savestring_table.append("")
            else:
                bwires_savestring = "+".join(_w.savestring_encode(block_indexes) for _w in w)
                savestring_table.append(bwires_savestring)

        return ",".join(savestring_table)
    
    def __repr__(self) -> str:
        return f"Building({self.name}, {self.building_type}, ...)"

class BuildingWire():
    def __init__(self, buidling: str, index: str | int, port: str, src: str):
        self.building = buidling
        self.index = index
        self.port = port
        self.src = src

    def savestring_encode(self, block_indexes: Dict[str, int]):
        return f"{Port[str.upper(self.port)]}{block_indexes[self.src]}"
    
    def __repr__(self):
        return (
            f"BuildingWire("
            f"building={self.building},"
            f"index={self.index},"
            f"port={str.upper(self.port)},"
            f"src={self.src}"
            f")"
        )

class Module:
    """
    Base module class.
    """
    def __init__(self, name: str="main"):
        self.name = name
        self.blocks: Dict[str, Union[Block, Array]] = {}
        self.wires: Dict[str, Wire] = {}
        self.buildings: Dict[str, Building] = {}
        self.ports: Dict[str, Any] = {}
        self.size = None

    def add(
        self,
        components: Component
    ):
        if not isinstance(components, List):
            components = [components]

        components = flatten_recursive(components)

        _blocks: List[Construct] = []
        _wires: List[Connection] = []

        for c in components:
            if isinstance(c, Wire) or isinstance(c, BuildingWire):
                _wires.append(c)
            else:
                c = cast(Construct, c)
                _blocks.append(c)

        for c in _blocks:
            if isinstance(c, Block):
                self.blocks[c.name] = c
            elif isinstance(c, Array):
                if c.width is None:
                    c.width = self.size
                self.blocks[c.name] = c
            elif isinstance(c, Module):
                self.merge(c)
            else: # Building
                self.buildings[c.name] = c


        for w in _wires:
            if isinstance(w, Wire):
                if w.src in self.blocks:         
                    src = self.blocks[w.src]
                else: # Probably a block from an array or array name from developed array
                    # Check if it is a developed array
                    if f"{w.src}.0" in self.blocks:
                        size = self.find_developed_array_size(w.src)
                        src = Array("", width=size)
                    else:
                        src = Block("") # Trust that it is a block from an array to be developed
                if w.dst in self.blocks:
                    dst = self.blocks[w.dst]
                else: # Probably a block from an array or array name from developed array
                    # Check if it is a developed array
                    if f"{w.dst}.0" in self.blocks:
                        size = self.find_developed_array_size(w.dst)
                        dst = Array("", width=size)
                    else:
                        dst = Block("") # Trust that it is a block from an array to be developed
                if isinstance(src, Array):
                    if isinstance(dst, Array):
                        src.width = cast(int, src.width)
                        dst.width = cast(int, dst.width)
                        max_pairs = min(src.width, dst.width)
                        if not w.inverted:
                            for i in range(max_pairs):
                                self.wires[f"{w.src}.{i}->{w.dst}.{i}"] = Wire(f"{w.src}.{i}", f"{w.dst}.{i}")
                        else:
                            for i in range(max_pairs):
                                self.wires[f"{w.src}.{i}->{w.dst}.{max_pairs - i - 1}"] = Wire(f"{w.src}.{i}", f"{w.dst}.{max_pairs - i - 1}")
                    else: # Block
                        src.width = cast(int, src.width)
                        for i in range(src.width):
                            self.wires[f"{w.src}.{i}->{w.dst}"] = Wire(f"{w.src}.{i}", f"{w.dst}")
                else: # Block
                    if isinstance(dst, Array):
                        dst.width = cast(int, dst.width)
                        for i in range(dst.width):
                            self.wires[f"{w.src}->{w.dst}.{i}"] = Wire(f"{w.src}", f"{w.dst}.{i}")
                    else: # Block
                        self.wires[f"{w.src}->{w.dst}"] = w
            else: # BuildingWire
                building: Building = self.buildings[w.building]
                building.add_wire(w)

    def remove(self, name: str):
        block = self.get_block(name)
        if block:
            del self.blocks[name]
            
        wire = self.get_wire(name)
        if wire:
            del self.wires[name]
            
        building = self.get_wire(name)
        if building:
            del self.buildings[name]

    def set_ports(self, value: Dict[str, Any]):
        assert len(value) > 0, "At least one port must be defined"
        self.ports = value

    def insert_port(self, name: str, port: str, index: Optional[int]):
        assert self.ports[port], f"Port '{port}' doesn't exist"

        if type(self.ports[port]) == List[str]:
            self.ports[port].append(name)
        else:
            assert self.ports[port][index], f"Index '{index}' of port '{port}' doesn't exist"
            assert type(self.ports[port][index]) == List[str], f"The chosen index '{index}' of port '{port}' is a nested list"
            self.ports[port][index].append(name)

    def set_size(self, size: int):
        """
        Set default arrays' size
        """
        self.size = size

    def move(self, move_vector: Tuple[float, float, float]):
        """
        Move the entire module by a relative position
        """
        for c in self.blocks.values():
            c.pos += Vector3(*move_vector)

    def rotate(self, rotation_matrix: List[List[float]], pivot: Tuple[float, float, float]):
        """
        Rotate the module by a rotation matrix over a pivot
        """
        for c in self.blocks.values():
            pos = np.array((c.pos.x, c.pos.y, c.pos.z))
            translated = pos - pivot
            rotated = np.dot(rotation_matrix, translated)
            c.pos = Vector3(*rotated) + Vector3(*pivot)

            if isinstance(c, Array):
                orientation = (
                    c.info.get("x_step"),
                    c.info.get("y_step"),
                    c.info.get("z_step")
                )
                orientation = cast(Tuple[float, float, float], orientation)
                rot_orientation = np.dot(rotation_matrix, orientation)
                c.info["x_step"]= rot_orientation[0]
                c.info["y_step"] = rot_orientation[1]
                c.info["z_step"] = rot_orientation[2]

    def auto_place(self):
        '''Auto place blocks based on ports'''
        i = 0

        for block in self.blocks.values():
            block.set_pos((0, 0, 0))

        if "input" in self.ports:
            i = 0
            for port in self.ports["input"]:
                if isinstance(port, list):
                    j = 0
                    # This is because hdl.py:parse_json_module generates reversed port blocks
                    _port = cast(List[str], port[::-1])
                    for p in _port:
                        block = self.get_block(p)
                        assert block, f"Block '{p}' from input port doesn't exist"
                        block.set_pos((j, i, 1))
                        j += 1
                else: # str
                    block = self.get_block(port)
                    assert block, f"Block '{port}' from input port doesn't exist"
                    block.set_pos((0, i, 1))
                i += 1
                
        if "output" in self.ports:
            i = 0
            for port in self.ports["output"]:
                if isinstance(port, list):
                    j = 0
                    _port = cast(List[str], port[::-1])
                    for p in _port:
                        block = self.get_block(p)
                        assert block, f"Block '{p}' from output port doesn't exist"
                        block.set_pos((j, i, -1))
                        j += 1
                else: # str
                    block = self.get_block(port)
                    assert block, f"Block '{port}' from output port doesn't exist"
                    block.set_pos((0, i, -1))
                i += 1

    def auto_balance(self) -> int:
        """This ensures all paths from any input to any output takes the same number of ticks"""
        assert "input" in self.ports, "Module doesn't have input port defined"
        assert "output" in self.ports, "Module doesn't have output port defined"
        
        graph = self.get_block_graph()
        module_outputs: List[str] = []
        for outputs in self.get_port("output"):
            _outputs = flatten_recursive(outputs)
            for p in _outputs:
                expanded = self.get_blocks_expanded(p)
                if expanded:
                    for block in expanded:
                        module_outputs.append(block.name) 
            
        def get_arrival_time(block: Block) -> int:
            times = get_input_arrival_times(block)
            if len(times) == 0:
                return 0
            else:
                return max(times.values())
       
        def get_input_arrival_times(block: Block) -> Dict[str, int]:
            inputs = graph[block.name]["inputs"]
            times: Dict[str, int] = {}
            for i in inputs:
                times[i["block"].name] = get_arrival_time(i["block"]) + 1
            return times
            
        def insert_input_delays(block: Block) -> int:
            times = get_input_arrival_times(block)
            slowest = get_arrival_time(block)
            
            for input_name, time in times.items():
                delay = slowest - time
                if delay > 0:
                    wire = self.get_wire(f"{input_name}->{block.name}")
                    if wire:
                        self.remove(f"{input_name}->{block.name}")
                        
                    this_id = random_id()
                    self.add([
                        Block(f"{input_name}.delay.{this_id}", "delay", properties=[f"{delay}"]),
                        Wire(f"{input_name}", f"{input_name}.delay.{this_id}"),
                        Wire(f"{input_name}.delay.{this_id}", block.name)
                    ])
            return slowest
        
        output_arrival_times: Dict[str, int] = {}
        
        nodes = graph.keys()
        for node in nodes:
            content = graph[node]
            arrival_time = insert_input_delays(content["block"])
            if content["block"].name in module_outputs:
                output_arrival_times[content["block"].name] = arrival_time
        
        slowest_output_arrival_time: int = max(output_arrival_times.values())
        for _output, time in output_arrival_times.items():
            delay = slowest_output_arrival_time - time
            
            if delay > 0:
                block = self.get_block(_output)
                if block:
                    block.block_id = "delay"
                    block.properties = [f"{delay}"]
                    
        return slowest_output_arrival_time
                    
    def def_ic(self):
        """Put IC terminals on module"""
        assert "input" in self.ports, "Module doesn't have input port defined"
        assert "output" in self.ports, "Module doesn't have output port defined"
        input_ports = flatten_recursive(self.ports["input"])
        output_ports = flatten_recursive(self.ports["output"])
        
        assert len(input_ports) <= 32, "Module has too many inputs"
        assert len(output_ports) <= 32, "Module has too many outputs"

        character = ord('A')
        for i in input_ports:
            self.add([
                Block(f"_IC_.input.{i}", "text", properties=[f"{character}"]),
                Block(f"_IC_.input.{i}.or", "or"),
                Wire(f"_IC_.input.{i}", f"_IC_.input.{i}.or"),
                Wire(f"_IC_.input.{i}.or", f"{i}")
            ])
            character += 1
            
        character = ord('A')
        for i in output_ports:
            self.add([
                Block(f"_IC_.output.{i}", "text", properties=[f"{character}"]),
                Block(f"_IC_.output.{i}.or", "or"),
                Wire(f"{i}", f"_IC_.output.{i}.or"),
                Wire(f"_IC_.output.{i}.or", f"_IC_.output.{i}")
            ])
            character += 1

    def get_port(self, port: str) -> List[Any]:
        """Returns list of elements in a port"""
        return self.ports[port]

    def get_center(self, ndigits: int = 0) -> Vector3:
        blocks = self.get_blocks()
        mean = Vector3(0, 0, 0)
        for block in blocks:
            mean += block.pos / len(blocks)

        return round(mean, ndigits)

    def get_dimensions(self):
        blocks = self.get_blocks()
        min_v = Vector3(0, 0, 0)
        max_v = Vector3(0, 0, 0)
        for block in blocks:
            min_v = min_v.elementwise_min(block.pos)
            max_v = max_v.elementwise_max(block.pos)
        dims = (max_v - min_v) + Vector3.ones()
        return dims

    def get_block_indexes(self) -> Dict[str, int]:
        block_indexes: Dict[str, int] = {}

        index = 1
        for c in self.blocks.values():
            if isinstance(c, Block):
                block_indexes[c.name] = index
                index += 1
            if isinstance(c, Array):
                array_blocks = c.get_blocks()
                for b in array_blocks.values():
                    block_indexes[b.name] = index
                    index += 1

        return block_indexes
    
    def get_blocks(self) -> List[Block]:
        blocks: List[Block] = []
        for c in self.blocks.values():
            if isinstance(c, Block):
                blocks.append(c)
            if isinstance(c, Array):
                array_blocks = c.get_blocks()
                for b in array_blocks.values():
                    blocks.append(b)

        return blocks

    def get_block_graph(self) -> Dict[str, Dict[str, Any]]:
        blocks: Dict[str, Dict[str, Any]] = {}
        for k, c in self.blocks.items():
            k: str
            if isinstance(c, Block):
                blocks[k] = {"block": c, "inputs": [], "outputs": []}
            if isinstance(c, Array):
                array_blocks = c.get_blocks()
                for j, b in array_blocks.items():
                    blocks[j] = {"block": b, "inputs": [], "outputs": []}
                    
        for w in self.wires.values():
            if w.src in blocks:
                dst_block = blocks[w.dst]
                blocks[w.src]["outputs"].append(dst_block)
            
            if w.dst in blocks:
                src_block = blocks[w.src]
                blocks[w.dst]["inputs"].append(src_block)

        return blocks
        

    def get_wires(self) -> List[Wire]:
        wires: List[Wire] = []
        for w in self.wires.values():
            wires.append(w)
        return wires

    def get_buildings(self) -> List[Building]:
        buildings: List[Building] = []
        for w in self.buildings.values():
            buildings.append(w)
        return buildings
    
    def get_block(self, name: str) -> Optional[Union[Block, Array]]:
        """
        Return a block/array component from self.blocks
        """
        return self.blocks.get(name)

    def get_blocks_expanded(self, name: str) -> Optional[List[Block]]:
        """Return a block or expanded list of blocks from an array"""
        component = self.blocks.get(name)
        if component:
            if isinstance(component, Array):
                return [block for block in component.get_blocks().values()]
            else:
                return [component]

    def get_wire(self, name: str) -> Optional[Wire]:
        """
        Return a wire component from self.wires
        """
        return self.wires.get(name)

    def get_building(self, name: str) -> Optional[Building]:
        """
        Return a building component from self.wires
        """
        return self.buildings.get(name)

    def find_developed_array_size(self, src: str) -> int:
        """
        Find the width of a developed array, an array that was
        created through blocks with enumerated names instead
        of using Array object.
        """
        bottom, top = 0, 32
        mid = 0
        while f"{src}.{top - 1}" in self.blocks:
            bottom = top
            top *= 2
        prev_mid = None
        while bottom < top:
            mid = (top + bottom) // 2
            if mid == prev_mid:
                break
            if f"{src}.{mid - 1}" in self.blocks:
                bottom = mid
            else:
                top = mid
            prev_mid = mid

        return mid

    def save(self, path: str):
        """Export module as a Circuit Maker 2 save string."""
        block_list = self.get_blocks()
        block_indexes = self.get_block_indexes()
        wire_list = self.get_wires()
        buildings_list = self.get_buildings()
        block_table = [b.savestring_encode() for b in block_list]
        wire_table = [w.savestring_encode(block_indexes) for w in wire_list]
        building_table = [bd.savestring_encode(block_indexes) for bd in buildings_list]
        #data_table = []
        
        # TODO: Custom build and data support

        string = ";".join(block_table) + "?" + ";".join(wire_table) + "?" + ";".join(building_table) +"?"
        
        with open(path, "w") as file:
            file.write(string)

        return string
    
    def merge(self, other: 'Module'):
        for name, component in other.blocks.items():
            component.name = f"{other.name}.{component.name}"
            self.blocks[f"{other.name}.{name}"] = component
        for name, wire in other.wires.items():
            self.wires[f"{other.name}.{name}"] = Wire(f"{other.name}.{wire.src}", f"{other.name}.{wire.dst}")

    def show_components(self, wires: bool = False):
        for k, b in self.blocks.items():
            print(f"{k}: {b}")

        if wires:
            for k, w in self.wires.items():
                print(f"{k}: {w}")
