#!/bin/sh

if [ $# -lt 3 ]; then
	echo "Usage: $0 <output> <top module> <verilog files...>" >&2
	exit 1
fi

output=$1
shift

top=$1
shift

echo "read_verilog -sv $*" > tmp.ys
echo "hierarchy -check -top $top" >> tmp.ys
cat cm2v.ys >> tmp.ys
echo "json -o $output" >> tmp.ys
yosys -s tmp.ys
rm tmp.ys
