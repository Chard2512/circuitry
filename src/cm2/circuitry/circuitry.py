"""
Circuit Maker 2 library for savestring generation and manipulation
"""

__author__ = "Chard"
__contact__ = "chardson.coelho17@gmail.com"
__copyright__ = "Copyright 2025, Chard2512"
__date__ = "2025/05/23"
__deprecated__ = False
__license__ = "MIT"
__maintainer__ = "Chard"
__status__ = "Production"
__version__ = "0.1.0-snapshot2"

from uuid import uuid4
from dataclasses import dataclass
from typing import List, TypedDict, Optional, Union, Tuple
import math
from enum import IntEnum
import base64

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
    def zero():
        return Vector3(0, 0, 0)

    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        return Vector3(self.x / length, self.y / length, self.z / length)
    
    def cross(self, other: 'Vector3'):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

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
    def __init__(self, block_id: int, pos: Vector3, state=False, properties=None):
        assert (
            isinstance(block_id, int) and 0 <= block_id <= 19
        ), "blockId must be an integer between 0 and 19"
        assert (
            isinstance(pos, Vector3)
        ), "pos must be a Vector3"
        assert isinstance(state, bool), "state must be a boolean"
        assert (
            isinstance(properties, list) or properties is None
        ), "properties must be a list of numbers, or None."
        self.block_id = block_id
        self.state = state
        self.pos = pos
        self.properties = properties
        self.uuid = str(uuid4())

    def savestring_encode(self):
        savestring_table = [
            str(self.block_id),
            ("1" if self.state else "0"),
            str(round(self.pos.x, 3)),
            str(round(self.pos.y, 3)),
            str(round(self.pos.z, 3)),
            ("" if not self.properties else "+".join(self.properties))
        ]
        return ",".join(savestring_table)
    
    def __repr__(self):
        block_name = BlockID(self.block_id)
        return (
            f"Block("
            f"block_id=Enum.Block.{block_name},"
            f"state={self.state},"
            f"pos={self.pos},"
            f"properties={self.properties},"
            f"uuid={self.uuid[:2]}..."
            f")"
        )
class Connection:
    def __init__(self, source, target):
        assert isinstance(source, Block), "source must be a Block object"
        assert isinstance(target, Block), "target must be a Block object"
        self.source = source
        self.target = target

    def savestring_encode(self, block_indexes):
        return f"{block_indexes[self.source.uuid]},{block_indexes[self.target.uuid]}"
    
    def __repr__(self):
        return f"Connection(source={self.source.uuid[:2]}...,target={self.target.uuid[:2]}...)"

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

class FindBlockInfo(TypedDict, total=False):
    block_id: Optional[int]
    search_box_pos: Optional[Vector3]
    search_box_dim: Optional[Vector3]
    state: Optional[bool]
    properties: Optional[List]

class Module:
    """
    Base module class.
    """
    def __init__(self):
        self.blocks = {}
        self.connections = {}
        self.buildings = {}

    def add_block(
        self,
        block_id: Union[int, str, BlockID],
        pos: Tuple[float, float, float] | Vector3,
        state: bool = False,
        properties: Optional[List[Union[int, float]]] = None,
        snap_to_grid: bool = True,
    ) -> Block:
        if isinstance(pos, tuple):
            pos = Vector3(*pos)
        """Add a block to the save."""
        if isinstance(block_id, str):
            block_id = BlockID[block_id.upper()]
        if isinstance(block_id, BlockID):
            block_id = block_id.value

        if snap_to_grid:
            new_block = Block(
                block_id,
                Vector3(
                    int(round(pos.x, 0)),
                    int(round(pos.y, 0)),
                    int(round(pos.z, 0)),
                ),
                state=state,
                properties=properties,
            )
        else:
            new_block = Block(block_id, pos, state=state, properties=properties)
        self.blocks[new_block.uuid] = new_block
        return new_block
    
    def add_array(
        self,
        width: int,
        block_id: Union[int, str, BlockID] ,
        pos: Tuple[float, float, float] | Vector3,
        state: bool = False,
        properties: Optional[List[Union[int, float]]] = None,
        info: Optional[ArrayInfo] = None
    ) -> List[Block]:
        if isinstance(block_id, str):
            block_id = BlockID[block_id.upper()]
        if isinstance(block_id, BlockID):
            block_id = block_id.value

        if isinstance(pos, tuple):
            pos = Vector3(*pos)

        """Add a block to the save."""
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
        info = default_info

        block_array = []
        for i in range(width):
            pos_offset = Vector3(
                (info["x_step"] * i  + info["x_cluster_space"] * (i // info["x_cluster"])) % info["x_cycle"],
                (info["y_step"] * i  + info["y_cluster_space"] * (i // info["y_cluster"])) % info["y_cycle"],
                (info["z_step"] * i  + info["z_cluster_space"] * (i // info["z_cluster"])) % info["z_cycle"],
            )
            if info["snap_to_grid"]:
                new_block = Block(
                    block_id,
                    Vector3(
                        int(round(pos.x + pos_offset.x, 0)),
                        int(round(pos.y + pos_offset.y, 0)),
                        int(round(pos.z + pos_offset.z, 0)),
                    ),
                    state=state,
                    properties=properties,
                )
            else:
                new_block = Block(block_id, pos + pos_offset, state=state, properties=properties)
            self.blocks[new_block.uuid] = new_block
            block_array.append(new_block)
        return block_array

    def connect_blocks(self, source: Block, target: Block) -> Connection:
        new_connection = Connection(source, target)
        if new_connection.target.uuid in self.connections:
            self.connections[new_connection.target.uuid].append(new_connection)
        else:
            self.connections[new_connection.target.uuid] = [new_connection]
        return new_connection
    
    def connect_arrays(
            self, 
            source_array: List[Block], 
            target_array: List[Block], 
            width: Optional[int] = None
    ) -> None:    
        if width is None:
            max_pairs = min(len(source_array), len(target_array))
        else:
            assert isinstance(width, int), "width should be an integer"
            assert width <= len(source_array), "width shouldn't be greater than source array length"
            assert width > 0, "width cannot be less than 1"
            max_pairs = min(width, len(target_array))
        
        for i in range(max_pairs):
            self.connect_blocks(source_array[i], target_array[i])

    def connect_one_to_many(self, src: Block, targets: List[Block]) -> None:
        """Connect one block to many (e.g., control signal to gates)."""
        for target in targets:
            self.connect_blocks(src, target)

    def delete_block(self, block: Block) -> None:
        """Delete a block from the save."""
        assert isinstance(block, Block), "block must be a Block object"
        assert block.uuid in self.blocks, "block does not exist in save"
        to_remove = []
        for key, conn_list in self.connections.items():
            self.connections[key] = [c for c in conn_list if c.source.uuid != block.uuid and c.target.uuid != block.uuid]
            if not self.connections[key]:
                to_remove.append(key)
        # Remove keys with empty connection lists
        for key in to_remove:
            del self.connections[key]
            
        del self.blocks[block.uuid]
        return

    def delete_connection(self, connection: Connection) -> None:
        """Delete a connection from the save."""
        assert isinstance(
            connection, Connection
        ), "connection must be a Connection object"
        assert connection in (n for c in self.connections.values() for n in c)
        for c in self.connections.values():
            for n in c:
                if connection == n:
                    del self.connections[n.target.uuid][
                        self.connections[n.target.uuid].index(n)
                    ]

    def find_block(self, criteria: FindBlockInfo) -> List[Block]:
        default_info: FindBlockInfo = {
            "block_id": None,
            "search_box_pos": None,
            "search_box_dim": None,
            "state": None,
            "properties": None,
        }

        if criteria is not None:
            default_info.update(criteria)
        criteria = default_info

        found_blocks = []

        for block in self.blocks.values():
            if criteria["block_id"] is not None and block.block_id != criteria["block_id"]:
                continue
            if criteria["properties"] is not None and block.properties != criteria["properties"]:
                continue
            if criteria["state"] is not None and block.state != criteria["state"]:
                continue
            if criteria["search_box_pos"] is not None:
                dim = criteria["search_box_dim"] or Vector3.zero()
                start = criteria["search_box_pos"]
                end = start + dim
                if not (min(start.x, end.x) <= block.pos.x <= max(start.x, end.x)):
                    continue
                if not (min(start.y, end.y) <= block.pos.y <= max(start.y, end.y)):
                    continue
                if not (min(start.z, end.z) <= block.pos.z <= max(start.z, end.z)):
                    continue
            found_blocks.append(block)

        return found_blocks

    def get_block_indexes(self):
        block_indexes = {}

        index = 1
        for b in self.blocks.values():
            block_indexes[b.uuid] = index
            index += 1

        return block_indexes

    def save(self, path):
        """Export module as a Circuit Maker 2 save string."""
        block_table = []
        connection_table = []
        #building_table = []
        #data_table = []
        block_indexes = self.get_block_indexes()

        for b in self.blocks.values():
            block_table.append(b.savestring_encode())

        for c in self.connections.values():
            for n in c:
                connection_table.append(n.savestring_encode(block_indexes))
        
        # TODO: Custom build and data support

        string = ";".join(block_table) + "?" + ";".join(connection_table) + "??"
        
        with open(path, "w") as file:
            file.write(string)

        return string

    def load(self, path: str, snap_to_grid=True) -> 'Module':
        """Import a Circuit Maker 2 save string as a module."""

        with open(path, "r") as file:
            string = file.read()

        sections = string.split("?")
        block_strings = sections[0].split(";")
        connection_strings = sections[1].split(";")

        blocks = []
        for block_string in block_strings:
            values = block_string.split(",")
            block_id = int(values[0])
            state = (values[1] == "1")
            pos = Vector3(float(values[2]), float(values[3]), float(values[4]))
            properties = []
            for v in values[5].split("+"):
                if v:
                    properties.append(float(v))
            if properties == []:
                properties = None

            blocks.append(self.add_block(
                block_id,
                pos,
                state,
                properties,
                snap_to_grid
            ))

        for connection_string in connection_strings:
            values = connection_string.split(",")
            block1 = blocks[int(values[0]) - 1]
            block2 = blocks[int(values[1]) - 1]
            self.connect_blocks(block1, block2)

        return self
    
    def merge(self, other: 'Module'):
        self.blocks.update(other.blocks)
        self.connections.update(other.connections)
        self.buildings.update(other.buildings)

    def show_components(self):
        block_indexes = self.get_block_indexes()

        for i, b in enumerate(self.blocks.values()):
            print(f"{i + 1}: {b}")

        for c in self.connections.values():
            for n in c:
                source_block_name = BlockID(self.blocks[n.source.uuid].block_id)
                target_block_name = BlockID(self.blocks[n.target.uuid].block_id)
                source_block_index = block_indexes[n.source.uuid]
                target_block_index = block_indexes[n.target.uuid]
                print(f"Connection({source_block_name} {source_block_index}, {target_block_name} {target_block_index})")

class CircuitBuilder:
    def __init__(self, module: Module):
        self.module = module
        self.named_components = {}  # Track named components for easy access

    def add(
        self,
        label: str = "",
        component_type: str = "block", 
        pos: Tuple[float, float, float] | Vector3 = (0, 0, 0), 
        block_id: Union[int, str, BlockID] = 0, 
        width = 1, 
        **kwargs):
        """Generalized method to add blocks/arrays."""
        if width > 1 or component_type == "array":
            blocks = self.module.add_array(
                width=width,
                block_id=block_id,
                pos=pos,
                **kwargs
            )
        else:
            blocks = self.module.add_block(block_id, pos, **kwargs)

        self.named_components[label] = blocks
        return self

    def connect(self, source: str = "", target: str = "", width: Optional[int]=None):
        """Generalized connection method."""
        src = self._get_component(source)
        tgt = self._get_component(target)
        
        if isinstance(src, list) and isinstance(tgt, list):
            self.module.connect_arrays(src, tgt, width)
        elif isinstance(tgt, list):
            self.module.connect_one_to_many(src, tgt)
        else:
            self.module.connect_blocks(src, tgt)
        return self

    def _get_component(self, ref) -> Block:
        """Resolve component reference (name string or object)"""
        if isinstance(ref, str):
            return self.named_components[ref]
        return ref