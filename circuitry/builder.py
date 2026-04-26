from .circuitry import *
from cm2.modules.stdm import *

def ArrayOf(
        component: list,
        width: int=None, 
        info: Optional["ArrayInfo"]=None,
    ):
    def convert_block_to_array(_list):
        new_list = []
        for component in _list:
            if isinstance(component, Block):
                new_component = Array(
                    component.name, 
                    component.block_id,
                    component.pos,
                    width,
                    info,
                    component.state,
                    component.properties)
                new_list.append(new_component)
            elif type(component) == list:
                convert_block_to_array(component)
            else:
                new_list.append(component)
        return new_list
    return convert_block_to_array(component)

def _make_gate(block_id: str):
    def gate(
        name: str, 
        outputs: list[str] | str = [],
        pos: Tuple[float, float, float] = (0, 0, 0), 
        state=False, 
        properties=None,
        delayed: Dict[str, int] = None,
        inverted: Dict[str, bool] = None, # For array connection
    ):
        if type(outputs) == str:
            outputs = [outputs]
        components = [Block(name, block_id, pos, state, properties)]
        for output in outputs:
            if delayed and output in delayed:
                delay_name = delay_name = f"{output[0]}._delay.{name}"
                components.append([
                    Block(delay_name, "delay", pos, properties=[str(delayed[output])]),
                    Wire(name, delay_name),
                    Wire(delay_name, output) if output not in inverted else
                    Wire(delay_name, output, inverted[output])
                ])
            else:
                components.append(Wire(name, output))
        return components
    
    return gate


# This is for linting purposes
def Nor(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=None, inverted=None): pass
def And(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Or(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Xor(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Button(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Flipflop(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Led(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Sound(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Conductor(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Custom(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Nand(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Xnor(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Random(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Text(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Tile(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Node(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Delay(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def Antenna(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def ConductorV2(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass
def LedMixer(name, outputs=[], pos=(0,0,0), state=True, properties=None, delayed=False, inverted=None): pass

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