"""cm2/modules/hdlm.py

Extended modules, used primarly by 'cm2/circuitry/hdl.py'
"""

from cm2.circuitry.builder import *

def DLatchP(name: str, pos: Tuple[float, float, float] = (0, 0, 0)):
    m = Module(name)
    m.set_ports({
        "input": ["D", "E"],
        "output": ["Q"]
    })
    m.add([
        Or("D", "pass"),
        Node("E", ["~E", "+E"]),

        Nor("~E", "trap"),
        Or("+E", "pass"),

        And("trap", "Q"),
        And("pass", "Q"),

        Node("Q", "trap")
    ])

    m.auto_place()
    m.move(pos)
    return m

def DLatchN(name: str, pos: Tuple[float, float, float] = (0, 0, 0)):
    m = Module(name)
    m.set_ports({
        "input": ["D", "E"],
        "output": ["Q"]
    })
    m.add([
        Or("D", "pass"),
        Node("E", ["~E", "+E"]),

        Nor("~E", "pass"),
        Or("+E", "trap"),

        And("trap", "Q"),
        And("pass", "Q"),

        Node("Q", "trap")
    ])

    m.auto_place()
    m.move(pos)
    return m

def DFFP(name: str, pos: Tuple[float, float, float] = (0, 0, 0)):
    m = Module(name)
    m.set_ports({
        "input": ["D", "C"],
        "output": ["Q"]
    })
    m.add([
        Or("D", "pass"),
        Node("C", ["~C", "+C"]),

        Nor("~C", "trap"),
        Or("+C", "pass"),

        And("trap", "Q"),
        And("pass", "Q"),

        Node("Q", "trap")
    ])

    m.auto_place()
    m.move(pos)
    return m