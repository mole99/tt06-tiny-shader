// SPDX-FileCopyrightText: © 2024 Leo Moser <https://codeberg.org/mole99>
// SPDX-License-Identifier: Apache-2.0

module icebreaker_top (
    input  logic CLK,

    // Built-in
    input  logic BTN_N,
    output logic LEDR_N,
    output logic LEDG_N,

    // PMOD 1A
    input  logic P1A1,
    input  logic P1A2,
    input  logic P1A3,
    input  logic P1A4,
    input  logic P1A7,
    input  logic P1A8,
    input  logic P1A9,
    input  logic P1A10,

    // PMOD 1B
    input  logic P1B1,
    input  logic P1B2,
    input  logic P1B3,
    input  logic P1B4,
    input  logic P1B7,
    input  logic P1B8,
    input  logic P1B9,
    input  logic P1B10,

    // PMOD 2
    output logic P2_1,
    output logic P2_2,
    output logic P2_3,
    output logic P2_4,
    output logic P2_7,
    output logic P2_8,
    output logic P2_9,
    output logic P2_10
);

    // Given input frequency:        12.000 MHz
    // Requested output frequency:   25.175 MHz
    // Achieved output frequency:    25.125 MHz

    logic locked;
    logic clk_25_175;

    SB_PLL40_PAD #(
		.FEEDBACK_PATH("SIMPLE"),
		.DIVR(4'b0000),		// DIVR =  0
		.DIVF(7'b1000010),	// DIVF = 66
		.DIVQ(3'b101),		// DIVQ =  5
		.FILTER_RANGE(3'b001)	// FILTER_RANGE = 1
	) uut (
		.LOCK(locked),
		.RESETB(1'b1),
		.BYPASS(1'b0),
		.PACKAGEPIN(CLK),
		.PLLOUTCORE(clk_25_175)
	);
	
    // Tiny Shader

    logic clk;
    logic rst_n;
    logic ena;
    logic [7:0] ui_in;
    logic [7:0] uio_in;
    logic [7:0] uo_out;
    logic [7:0] uio_out;
    logic [7:0] uio_oe;
    
    tt_um_tiny_shader_mole99 tt_um_tiny_shader_mole99_inst (
        .ui_in  (ui_in),    // Dedicated inputs
        .uo_out (uo_out),   // Dedicated outputs
        .uio_in (uio_in),   // IOs: Input path
        .uio_out(uio_out),  // IOs: Output path
        .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
        .ena    (ena),      // enable - goes high when design is selected
        .clk    (clk),      // clock
        .rst_n  (rst_n)     // not reset
    );
    
    // Assignments
    
    assign ena = 1'b1;
    assign rst_n = BTN_N && locked;
    assign clk = clk_25_175;
    
    // Output PMOD - Tiny VGA

    assign {P2_1, P2_7} = {uo_out[0], uo_out[4]};
    assign {P2_2, P2_8} = {uo_out[1], uo_out[5]};
    assign {P2_3, P2_9} = {uo_out[2], uo_out[6]};
    
    assign P2_4 = uo_out[3];
    assign P2_10 = uo_out[7];
    
    // Bidir PMOD - SPI and additional signals
    
    // Top row - SPI
    assign uio_in[0] = 1'b0;
    assign uio_in[1] = 1'b0;
    //assign TODO = uio_out[2];
    assign uio_in[3] = 1'b0;

    // Input PMOD - mode
    
    assign ui_in[0] = 1'b0;
		
endmodule
