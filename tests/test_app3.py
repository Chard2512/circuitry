from src.cm2.circuitry import *
from src.cm2.stdm import Flipflop

main = Module("main")

main.add([
    Flipflop("ff1", 16, (0, 0, 0)),
    Flipflop("ff2", 16, (0, 0, -4)),
    Wire("ff1.output", "ff2.input")
])

main.save("tests/file.txt")