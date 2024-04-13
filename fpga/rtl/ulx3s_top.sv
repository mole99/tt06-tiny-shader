// SPDX-FileCopyrightText: © 2022 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`timescale 1ns/1ps
`default_nettype none

module ulx3s_top (
    input clk_25mhz,

    input  [6:0] btn,
    output [7:0] led,

    output logic [27:0] gn,
    output logic [27:0] gp
);
    logic reset_n;
    assign reset_n = btn[0];
    
    logic [24-1:0] counter;
    
    always_ff @(posedge clk_25mhz, negedge reset_n) begin
        if (!reset_n) begin
            counter <= '0;
        end else begin
            counter <= counter + 1;
        end
    end
    
    assign led[0] = counter[24-1];
    assign led[1] = !counter[24-1];

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
    assign rst_n = reset_n;
    assign clk = clk_25mhz;
    
    // Output PMOD - Tiny VGA

    assign R[1] = uo_out[0];
    assign G[1] = uo_out[1];
    assign B[1] = uo_out[2];
    assign vsync = uo_out[3];
    assign R[0] = uo_out[4];
    assign G[0] = uo_out[5];
    assign B[0] = uo_out[6];
    assign hsync = uo_out[7];
    
    // Bidir PMOD - SPI and additional signals
    
    // Top row - SPI
    assign uio_in[0] = 1'b0;
    assign uio_in[1] = 1'b0;
    //assign TODO = uio_out[2];
    assign uio_in[3] = 1'b0;

    // Input PMOD - mode
    
    assign ui_in[0] = 1'b0;
    
    wire [1:0] R;
    wire [1:0] G;
    wire [1:0] B;
    wire hsync, vsync;

    assign gn[21] = vsync; assign gp[21] = hsync;
    assign gn[22] = B[1]; assign gp[22] = B[0];
    assign gn[23] = G[1]; assign gp[23] = G[0];
    assign gn[24] = R[1]; assign gp[24] = R[0];

endmodule
