"""
Circuit Maker 2 library for savestring generation and manipulation
"""

__author__ = "Chard"
__contact__ = "chardson.coelho17@gmail.com"
__copyright__ = "Copyright 2025, Chard2512"
__date__ = "2025/05/27"
__deprecated__ = False
__license__ = "MIT"
__maintainer__ = "Chard"
__status__ = "Production"
__version__ = "0.1.0-snapshot4"

import numpy as np
from dataclasses import dataclass, field
from typing import cast, List, TypedDict, Optional, Tuple, Dict, Union
import math
from enum import IntEnum, Enum
from types import MappingProxyType

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
        "output_index": 16,
        "value_index": 32,
        "write_index": 48
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
    def zeros():
        return Vector3(0, 0, 0)
    
    @staticmethod
    def ones():
        return Vector3(1, 1, 1)

    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        return Vector3(self.x / length, self.y / length, self.z / length)
    
    def cross(self, other: 'Vector3'):
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

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __truediv__(self, other):
        return Vector3(self.x / other, self.y / other, self.z / other)
    
    def __mul__(self, other):
        return Vector3(self.x * other, self.y * other, self.z * other)
    
    def __round__(self, ndigits=0):
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
    def angles(euler_angles: Tuple[float, float, float]) -> List[List[float]]:
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

        R = Rz @ Ry @ Rx
        # Necessary unnecessary statement, because linter fears this gonna be a bool instead of a list
        R_list = cast(List[List[float]], R.tolist())
        return R_list

    def __repr__(self):
        return f"CFrame(pos={self.pos}, rot={self.rot})"

class Block:
    def __init__(
            self, 
            name: str, 
            block_id: str="node", 
            pos: Tuple[float, float, float] | Vector3=(0, 0, 0), 
            state=False, 
            properties=None
    ):
        if isinstance(pos, Tuple):
            pos = Vector3(*pos)
        self.name = name
        self.block_id = block_id
        self.state = state
        self.pos = pos
        self.properties = properties

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
        width: int, 
        block_id: str="node", 
        pos: Tuple[float, float, float] | Vector3=(0, 0, 0),
        info: Optional["ArrayInfo"]=None,
        state=False, 
        properties=None
    ):
        if isinstance(pos, Tuple):
            pos = Vector3(*pos)
        self.name = name
        self.width = width 
        self.block_id = block_id
        self.pos = pos
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

    def get_blocks(self) -> Dict:
        blocks = {}
        info = self.info
        for i in range(self.width):
            pos_offset = Vector3(
                (info["x_step"] * i  + info["x_cluster_space"] * (i // info["x_cluster"])) % info["x_cycle"],
                (info["y_step"] * i  + info["y_cluster_space"] * (i // info["y_cluster"])) % info["y_cycle"],
                (info["z_step"] * i  + info["z_cluster_space"] * (i // info["z_cluster"])) % info["z_cycle"],
            )
            block_pos = self.pos + pos_offset
            blocks[f"{self.name}{i}"] = Block(
                f"{self.name}{i}",
                self.block_id,
                block_pos,
                self.state,
                self.properties
            )
        
        return blocks

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
    def __init__(self, src: str, dst: str):
        self.src = src
        self.dst = dst

    def savestring_encode(self, block_indexes):
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
        cframe: CFrame | Tuple[float, float, float],
        nwires: int = 0
    ):
        if isinstance(cframe, Tuple):
            cframe = CFrame(cframe)
        self.name = name
        self.building_type = building_type
        self.cframe: CFrame = cframe
        if str.upper(self.building_type) in BuildingData.__members__:
            nwires = int(BuildingData[str.upper(self.building_type)].value["nwires"])
        self.wires = [[] for _ in range(nwires)]

    def add_wire(self, building_wire: 'BuildingWire'):
        if isinstance(building_wire.index, str):
            index = int(BuildingData[self.building_type].value[f"{building_wire.index}_index"])
        else:
            index = building_wire.index

        self.wires[index].append(building_wire)

    def savestring_encode(self, block_indexes):
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
            elif isinstance(w, List):
                bwires_savestring = "+".join(_w.savestring_encode(block_indexes) for _w in w)
                savestring_table.append(bwires_savestring)

        return ",".join(savestring_table)
    
    def __repr__(self):
        return (
            f"Building("
            f"{self.building_type}",
            f"{self.cframe.pos}",
            f"{self.cframe.rot}"
            f")"
        )

class BuildingWire():
    def __init__(self, buidling: str, index: str | int, port: str, src: str):
        self.building = buidling
        self.index = index
        self.port = port
        self.src = src

    def savestring_encode(self, block_indexes):
        return f"{Port[str.upper(self.port)]}{block_indexes[self.src]}"

class Module:
    """
    Base module class.
    """
    def __init__(self, name: Optional[str]="main"):
        self.name = name
        self.blocks = {}
        self.wires = {}
        self.buildings = {}

    def add(
        self,
        components: List[Union[Block, Array, Wire, "Module", Building, BuildingWire]]
    ):
        for c in components:
            if isinstance(c, Block | Array):
                self.blocks[c.name] = c
            if isinstance(c, Wire):
                if c.src in self.blocks:
                    src = self.blocks[c.src]
                else: # Probably a block from an array or array name from developed array
                    # Check if it is a developed array
                    if f"{c.src}0" in self.blocks:
                        size = self.find_developed_array_size(c.src)
                        src = Array("", size, "")
                    else:
                        src = Block("", "") # Trust that it is a block from an array to be developed
                if c.dst in self.blocks:
                    dst = self.blocks[c.dst]
                else: # Probably a block from an array or array name from developed array
                    # Check if it is a developed array
                    if f"{c.dst}0" in self.blocks:
                        size = self.find_developed_array_size(c.dst)
                        dst = Array("", size, "")
                    else:
                        dst = Block("", "") # Trust that it is a block from an array to be developed
                if isinstance(src, Array):
                    if isinstance(dst, Array):
                        max_pairs = min(src.width, dst.width)
                        for i in range(max_pairs):
                            self.wires[f"{c.src}{i}->{c.dst}{i}"] = Wire(f"{c.src}{i}", f"{c.dst}{i}")
                elif isinstance(src, Block):
                    if isinstance(dst, Array):
                        for i in range(dst.width):
                            self.wires[f"{c.src}->{c.dst}{i}"] = Wire(f"{c.src}", f"{c.dst}{i}")
                    elif isinstance(dst, Block):
                        self.wires[f"{c.src}->{c.dst}"] = c
            if isinstance(c, Module):
                self.merge(c)
            if isinstance(c, Building):
                self.buildings[c.name] = c
            if isinstance(c, BuildingWire):
                building: Building = self.buildings[c.building]
                building.add_wire(c)

    def move(self, move_vector: Tuple[float, float, float] | Vector3):
        if isinstance(move_vector, Tuple):
            move_vector = Vector3(*move_vector)
        for c in self.blocks.values():
            c.pos += move_vector

    def get_center(self, ndigits=0) -> Vector3:
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

    def get_block_indexes(self):
        block_indexes = {}

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
    
    def get_blocks(self):
        blocks = []
        for c in self.blocks.values():
            if isinstance(c, Block):
                blocks.append(c)
            if isinstance(c, Array):
                array_blocks = c.get_blocks()
                for b in array_blocks.values():
                    blocks.append(b)

        return blocks

    def get_wires(self):
        wires = []
        for w in self.wires.values():
            wires.append(w)
        return wires

    def get_buildings(self):
        buildings = []
        for w in self.buildings.values():
            buildings.append(w)
        return buildings
    
    def find_developed_array_size(self, src):
        """
        Find the width of a developed array, an array that was
        created through blocks with enumerated names instead
        of using Array object.
        """
        bottom, top = 0, 32
        while f"{src}{top - 1}" in self.blocks:
            bottom = top
            top *= 2
        prev_mid = None
        while bottom < top:
            mid = (top + bottom) // 2
            if mid == prev_mid:
                break
            if f"{src}{mid - 1}" in self.blocks:
                bottom = mid
            else:
                top = mid
            prev_mid = mid

        return mid

    def save(self, path):
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

    def show_components(self, wires=False):
        for k, b in self.blocks.items():
            print(f"{k}: {b}")

        if wires:
            for k, w in self.wires.items():
                print(f"{k}: {w}")
