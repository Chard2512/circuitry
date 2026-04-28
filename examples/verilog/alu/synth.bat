@echo off

if "%1"=="" goto :usage
if "%2"=="" goto :usage
if "%3"=="" goto :usage

set output=%1
shift

set top=%1
shift

echo read_verilog -sv %* > tmp.ys
echo hierarchy -check -top %top% >> tmp.ys
type cm2v.ys >> tmp.ys
echo json -o %output% >> tmp.ys
yosys -s tmp.ys
del tmp.ys
goto :eof

:usage
echo Usage: %0 ^<output^> ^<top module^> ^<verilog files...^>
exit /b 1