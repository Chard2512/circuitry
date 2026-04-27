"""cm2/circuitry/builder.py

Defines an easier interface for blocks/arrays/wire building, abstracting on top of 'core.py'.
"""

from .core import *
from cm2.modules.stdm import *

def ArrayOf(
        component: List[PrimitiveComponent],
        width: Optional[int] = None, 
        info: Optional["ArrayInfo"] = None,
    ) -> List[PrimitiveComponent]:
    def convert_block_to_array(_list: List[Any]) -> List[Any]:
        new_list: List[PrimitiveComponent] = []
        for component in _list:
            if isinstance(component, Block):
                new_component = Array(
                    component.name, 
                    component.block_id,
                    (component.pos.x, component.pos.y, component.pos.z),
                    width,
                    info,
                    component.state,
                    component.properties)
                new_list.append(new_component)
            elif type(component) == List[PrimitiveComponent]:
                convert_block_to_array(component)
            new_list.append(component)
        return new_list
    return convert_block_to_array(component)

def _make_gate(block_id: str):
    def gate(
        name: str, 
        outputs: List[str] | str = [],
        pos: Tuple[float, float, float] = (0, 0, 0), 
        state: bool = False, 
        properties: Optional[List[str]] = None,
        delayed: Optional[Dict[str, int]] = None,
        inverted: Optional[Dict[str, bool]] = None, # For array connection
    ) -> List[PrimitiveComponent]:
        if type(outputs) == str:
            outputs = [outputs]
        components: List[Any] = [Block(name, block_id, pos, state, properties)]
        if outputs:
            for output in outputs:
                if delayed and output in delayed:
                    delay_name = delay_name = f"{output[0]}._delay.{name}"
                    components.append([
                        Block(delay_name, "delay", pos, properties=[str(delayed[output])]),
                        Wire(name, delay_name),
                        Wire(delay_name, output) if not inverted or (not output in inverted) else
                        Wire(delay_name, output, inverted[output])
                    ])
                else:
                    components.append(Wire(name, output))
        return components

    return gate

# This looks horrible, but at least IDE will understand these as functions (color them).
# Besides, this hardly gonna change anyways, and adding more blocks wouldn't be that
# much trouble.

def Nor(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("nor")(name, outputs, pos, state, properties, delayed, inverted)

def And(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("and")(name, outputs, pos, state, properties, delayed, inverted)

def Or(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("or")(name, outputs, pos, state, properties, delayed, inverted)

def Xor(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("xor")(name, outputs, pos, state, properties, delayed, inverted)

def Button(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("button")(name, outputs, pos, state, properties, delayed, inverted)

def Flipflop(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("flipflop")(name, outputs, pos, state, properties, delayed, inverted)

def Led(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("led")(name, outputs, pos, state, properties, delayed, inverted)

def Sound(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("sound")(name, outputs, pos, state, properties, delayed, inverted)

def Conductor(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("conductor")(name, outputs, pos, state, properties, delayed, inverted)

def Custom(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("custom")(name, outputs, pos, state, properties, delayed, inverted)

def Nand(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("nand")(name, outputs, pos, state, properties, delayed, inverted)

def Xnor(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("xnor")(name, outputs, pos, state, properties, delayed, inverted)

def Random(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("random")(name, outputs, pos, state, properties, delayed, inverted)

def Text(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("text")(name, outputs, pos, state, properties, delayed, inverted)

def Tile(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("tile")(name, outputs, pos, state, properties, delayed, inverted)

def Node(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("node")(name, outputs, pos, state, properties, delayed, inverted)

def Delay(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("delay")(name, outputs, pos, state, properties, delayed, inverted)

def Antenna(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("antenna")(name, outputs, pos, state, properties, delayed, inverted)

def ConductorV2(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("conductor_v2")(name, outputs, pos, state, properties, delayed, inverted)

def LedMixer(
    name: str,
    outputs: List[str] | str = [],
    pos: Tuple[float, float, float] = (0, 0, 0),
    state: bool = False,
    properties: Optional[List[str]] = None,
    delayed: Optional[Dict[str, int]] = None,
    inverted: Optional[Dict[str, bool]] = None
) -> List[PrimitiveComponent]:
    return _make_gate("led_mixer")(name, outputs, pos, state, properties, delayed, inverted)