from src.cm2.circuitry import *
from src.cm2.stdm import Decoder

m = Module("main")

m.add([
    Decoder("dc", 7, (0, 0, 0)),
    Block("node", "node", (0, 0, -15)),
    Wire("dc.output0", "node")
])

m.save("tests/file.txt")