all : resume_sim.tex text_gen.svg

verif : resume_sim.tex 

ifeq (, $(shell which python))
$(error "No python in $(PATH), please install python, used to generate verilog.")
endif

ifeq (, $(shell which iverilog))
$(error "No iverilog in $$PATH, please install icarus verilog, used to run simulation.")
endif

ifeq (, $(shell which yosys))
$(error "No yosys in $$PATH, please install yosys synthesis tool, used to generate netlist and json representation.")
endif

ifeq (, $(shell which netlistsvg))
$(error "No netlistsvg in $$PATH, please install netlistsvg, used to convert json to svg.")
endif

text_gen.v : resume.tex gen_text.py 
	python gen_text.py resume.tex 

sim_exe : tb_text_gen.v text_gen.v 
	#$(info iverilog :  $(shell which iverilog))
	iverilog -s tb_text_gen tb_text_gen.v text_gen.v -o sim_exe

resume_sim.tex : sim_exe 
	./sim_exe | grep -v "VCD info: dumpfile" > resume_sim.tex

text_gen.json : synth_circuit.yosys text_gen.v
	yosys -s synth_circuit.yosys > synth_circuit.log
   
text_gen.svg : text_gen.json
	netlistsvg text_gen.json -o text_gen.svg

