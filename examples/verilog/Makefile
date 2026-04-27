PYTHON = python
SYNTHESIZER = synth.sh
COMPILER = compile.py

# Set your project name here
PROJECT_NAME = ALU

# This is the top module in the verilog, change it to whatever you'd like.
# If you let like this, the name of the entry module should match the
# project's name.
ENTRY_MODULE = $(PROJECT_NAME) 

VERILOG_FILES = $(wildcard src/*.v)
SYNTH_OUTPUT = build/${PROJECT_NAME}.json

# This is the output path of the savestring
COMP_OUTPUT = build/${PROJECT_NAME}.txt 

all: clean $(COMP_OUTPUT)

$(COMP_OUTPUT): $(SYNTH_OUTPUT)
	$(PYTHON) $(COMPILER) $(SYNTH_OUTPUT) $(ENTRY_MODULE) $(COMP_OUTPUT)

$(SYNTH_OUTPUT):
	./$(SYNTHESIZER) $(SYNTH_OUTPUT) $(ENTRY_MODULE) $(VERILOG_FILES)

clean:
	@rm -f build/*
