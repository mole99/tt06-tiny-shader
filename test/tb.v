`default_nettype none
`timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

    // Dump the signals to a VCD file. You can view it with gtkwave.
    initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    $dumpvars(0, tb.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.shader_execute_inst.regs[0]);
    $dumpvars(0, tb.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.shader_execute_inst.regs[1]);
    $dumpvars(0, tb.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.shader_execute_inst.regs[2]);
    $dumpvars(0, tb.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.shader_execute_inst.regs[3]);
    #1;
    end

    // Wire up the inputs and outputs:
    reg clk;
    reg rst_n;
    reg ena;
    reg [7:0] ui_in;
    reg [7:0] uio_in;
    wire [7:0] uo_out;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;

    // Assign to peripherals

    wire [5:0] rrggbb;
    wire hsync;
    wire vsync;

    // Output PMOD - Tiny VGA

    assign rrggbb[5:4] = {uo_out[0], uo_out[4]};
    assign rrggbb[3:2] = {uo_out[1], uo_out[5]};
    assign rrggbb[1:0] = {uo_out[2], uo_out[6]};
    
    assign vsync = uo_out[3];
    assign hsync = uo_out[7];


    // Replace tt_um_example with your module name:
    tt_um_tiny_shader_mole99 tt_um_tiny_shader_mole99_inst (

        // Include power ports for the Gate Level test:
`ifdef GL_TEST
        .VPWR(1'b1),
        .VGND(1'b0),
`endif

        .ui_in  (ui_in),    // Dedicated inputs
        .uo_out (uo_out),   // Dedicated outputs
        .uio_in (uio_in),   // IOs: Input path
        .uio_out(uio_out),  // IOs: Output path
        .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
        .ena    (ena),      // enable - goes high when design is selected
        .clk    (clk),      // clock
        .rst_n  (rst_n)     // not reset
    );

endmodule
