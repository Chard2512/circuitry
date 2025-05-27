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
__version__ = "0.1.0-snapshot3"

from dataclasses import dataclass
<<<<<<< HEAD
from typing import List, TypedDict, Optional, Union, Tuple
=======
from typing import List, TypedDict, Optional, Tuple, Dict, Union
>>>>>>> trying-idea
import math
from enum import IntEnum

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
    """Data class to represent position and rotation"""
    def __init__(self, position: Vector3, rotation=None):
        self.position = position
        self.rotation = rotation or self.identity_matrix()

    @staticmethod
    def identity_matrix():
        return [
            [1, 0, 0],  # Right
            [0, 1, 0],  # Up
            [0, 0, 1]   # Backward
        ]

    @classmethod
    def look_at(cls, from_pos: Vector3, to_pos: Vector3):
        forward = (to_pos - from_pos).normalize()
        up = Vector3(0, 1, 0)
        right = up.cross(forward).normalize()
        up = forward.cross(right).normalize()

        rotation = [
            [right.x, right.y, right.z],
            [up.x, up.y, up.z],
            [forward.x, forward.y, forward.z]
        ]

        return cls(from_pos, rotation)

    def __repr__(self):
        return f"CFrame(pos={self.position}, rot={self.rotation})"

class Block:
    def __init__(
            self, 
            name: str, 
            block_id: str, 
            pos: Tuple[float, float, float] | Vector3, 
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
        block_id: str, 
        pos: Tuple[float, float, float] | Vector3,
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
        components: List[Union[Block, Array, Wire, "Module"]]
    ):
        for c in components:
            if isinstance(c, Block | Array):
                self.blocks[c.name] = c
            if isinstance(c, Wire):
                if c.src in self.blocks:
                    src = self.blocks[c.src]
                else:
                    src = Block("", "", (0, 0, 0)) # Trust that it is from an array to be developed
                if c.dst in self.blocks:
                    dst = self.blocks[c.dst]
                else:
                    dst = Block("", "", (0, 0, 0)) # Trust that it is from an array to be developed
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

    def save(self, path):
        """Export module as a Circuit Maker 2 save string."""
        block_list = self.get_blocks()
        block_indexes = self.get_block_indexes()
        wire_list = self.get_wires()
        block_table = [b.savestring_encode() for b in block_list]
        wire_table = [w.savestring_encode(block_indexes) for w in wire_list]
        #building_table = []
        #data_table = []
        
        # TODO: Custom build and data support

        string = ";".join(block_table) + "?" + ";".join(wire_table) + "??"
        
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
        block_indexes = self.get_block_indexes()

        for k, b in self.blocks.items():
            print(f"{k}: {b}")

        if wires:
            for k, w in self.wires.items():
                print(f"{k}: {w}")
