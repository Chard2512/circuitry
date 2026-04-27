# Circuitry

A Circuit Maker 2 (Roblox) library that enables savestring construction through various abstraction levels, including support for Hardware Description Languages, such as Verilog.

## Dependencies

The following must be in your `PATH`:

- Python 3

For Verilog support:

- Yosys 0.64
- Make (for automated Verilog compilation at `examples/verilog`)

## Levels of abstraction

### cm2/circuitry/core.py

This file provides the heart of the library, with the most essential classes for module manipulation. On the beginning of the project, this was the only way of coding, but now it's *deprecated* to code on this level, unless it is really necessary or there is some function there that you need to use.

All modules written at `cm2/modules/stdm.py` was written solely at this level. Check it out for some examples of usage.

### cm2/circuitry/builder.py

Currently recommended level for full control support. The purpose of this file is to provide some abstraction on top of `core.py`, so it's easier to build modules. Most functions will return a list of components that work together, instead of adding them one by one.

From now on, all pre written modules on the library will be written at this level. Check out `cm2/modules/hdlm.py` for some usage examples.

### cm2/circuitry/hdl.py

This is the newest, experimental and highest abstraction level, based of coding Modules via Hardware Description Languages, with main support to Yosys 0.64. The current recommended language is Verilog, as all testing was done one this language, but it can have support to other languages in the future.

This level is experimental, so it doesn't have full support and may have bugs. However, it currently can generate both combinatorial and sequential circuits.