default: openlane

RTL = src/tt_um_tiny_shader_mole99.sv \
      src/tiny_shader_top.sv \
      src/shader_execute.sv \
      src/shader_memory.sv \
      src/spi_receiver.sv \
      src/timing.sv \
      src/synchronizer.sv

FPGA_ICEBREAKER = fpga/rtl/icebreaker_top.sv

FPGA_ULX3S = fpga/rtl/ulx3s_top.sv \
	     fpga/rtl/pll40m.v

# Simulation

sim-icarus:
	iverilog -g2012 -o top.vvp $(RTL) tb/tb_icarus.sv
	vvp top.vvp -fst

sim-icarus-gl:
	iverilog -g2012 -s tb -o top.vvp $(GL) tb/tb_icarus_gl.sv -DUSE_POWER_PINS=1
	vvp top.vvp -fst

sim-verilator:
	verilator --cc --exe --build -j 0 -Wall $(RTL) tb/tb_verilator.cpp -LDFLAGS "-lSDL2 -lpng16"
	./obj_dir/Vtop

sim-cocotb:
	python3 tb/tb_cocotb.py

# Software

sw:
	make -C sw/
.PHONY: sw

# FPGA

# --- iCEBreaker ---

synth-icebreaker: icebreaker.json

build-icebreaker: icebreaker.bit

upload-icebreaker: icebreaker.bit
	openFPGALoader --board=ice40_generic -f icebreaker.bit

icebreaker.json: $(RTL) $(FPGA_ICEBREAKER)
	yosys -l $(basename $@)-yosys.log -DSYNTHESIS -DICEBREAKER -p 'synth_ice40 -top icebreaker_top -json $@' $^

icebreaker.asc: icebreaker.json
	nextpnr-ice40 --up5k --json $< \
		--pcf fpga/constraints/icebreaker.pcf \
		--package sg48 \
		--asc $@

icebreaker.bit: icebreaker.asc
	icepack $< $@

# --- ULX3S ---
# TODO not tested!

synth-ulx3s: ulx3s.json

build-ulx3s: ulx3s.bit

upload-ulx3s: ulx3s.bit
	openFPGALoader --board=ulx3s -f ulx3s.bit

ulx3s.json: $(RTL) $(FPGA_ULX3S)
	yosys -l $(basename $@)-yosys.log -DSYNTHESIS -DULX3S -DMODE_800x600 -p 'synth_ecp5 -top ulx3s_top -json $@' $^

ulx3s.config: ulx3s.json fpga/constraints/ulx3s_v20.lpf
	nextpnr-ecp5 --85k --json $< \
		--lpf fpga/constraints/ulx3s_v20.lpf \
		--package CABGA381 \
		--textcfg $@

ulx3s.bit: ulx3s.config
	ecppack $< $@ --compress

clean:
	rm -f *.vvp *.vcd
	rm -f icebreaker.json icebreaker.asc icebreaker.bit icebreaker-yosys.log
	rm -f ulx3s.json ulx3s.config ulx3s.bit ulx3s-yosys.log

.PHONY: clean sim-icarus sim-verilator sim-cocotb sprites
