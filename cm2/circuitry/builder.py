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

Nor = _make_gate("nor")
And = _make_gate("and")
Or = _make_gate("or")
Xor = _make_gate("xor")
Button = _make_gate("button")
Flipflop = _make_gate("flipflop")
Led = _make_gate("led")
Sound = _make_gate("sound")
Conductor = _make_gate("conductor")
Custom = _make_gate("custom")
Nand = _make_gate("nand")
Xnor = _make_gate("xnor")
Random = _make_gate("random")
Text = _make_gate("text")
Tile = _make_gate("tile")
Node = _make_gate("node")
Delay = _make_gate("delay")
Antenna = _make_gate("antenna")
ConductorV2 = _make_gate("conductor_v2")
LedMixer = _make_gate("led_mixer")