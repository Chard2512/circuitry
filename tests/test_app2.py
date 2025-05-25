from src.cm2.circuitry import *
from src.cm2.utils import create_flipflop

m = Module()

create_flipflop(m, "flipflop", 16)

m.save("tests/file.txt")