// SPDX-FileCopyrightText: © 2022 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module spi_receiver #(
    parameter REG_SIZE = 8,
    parameter [REG_SIZE-1:0] REG_DEFAULT = '0
)(
    input  logic clk_i,    // clock
    input  logic rst_ni,   // reset active low
    
    // SPI signals
    input  logic spi_sclk_i,
    input  logic spi_mosi_i,
    output logic spi_miso_o,
    input  logic spi_cs_i,
    
    // Mode signal
    // '0' = command mode
    // '1' = data mode
    input  logic       mode_i,
    
    // Output memory
    output logic [7:0] memory_instr_o,  // current sprite data
    output logic       memory_shift_o,  // shift pulse
    output logic       memory_load_o,   // shift new data into sprite
    
    // Output user register
    output logic [REG_SIZE-1:0] user_o
);
    
    logic [REG_SIZE-1:0] user;
    
    // Synchronizer to prevent metastability

    logic spi_mosi_sync;
    synchronizer  #(
        .FF_COUNT(2)
    ) synchronizer_spi_mosi (
        .clk        (clk_i),
        .reset_n    (rst_ni),
        .in         (spi_mosi_i),
        .out        (spi_mosi_sync)
    );

    logic spi_cs_sync;
    synchronizer  #(
        .FF_COUNT(2)
    ) synchronizer_spi_cs (
        .clk        (clk_i),
        .reset_n    (rst_ni),
        .in         (spi_cs_i),
        .out        (spi_cs_sync)
    );

    logic spi_sclk_sync;
    synchronizer  #(
        .FF_COUNT(2)
    ) synchronizer_spi_sclk (
        .clk        (clk_i),
        .reset_n    (rst_ni),
        .in         (spi_sclk_i),
        .out        (spi_sclk_sync)
    );

    // Detect spi_clk edge
    
    logic spi_sclk_delayed;
    always_ff @(posedge clk_i) begin
        spi_sclk_delayed <= spi_sclk_sync;
    end
    
    logic spi_sclk_falling, spi_sclk_rising;
    assign spi_sclk_rising = !spi_sclk_delayed && spi_sclk_sync;
    assign spi_sclk_falling = spi_sclk_delayed && !spi_sclk_sync;
    
    // State Machine
    logic [7:0] spi_cmd;
    logic [2:0] spi_cnt;
    
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            spi_cnt  <= 3'd0;
            user <= REG_DEFAULT;
            spi_cmd <= '0;
            spi_miso_o <= 1'b0;

            memory_shift_o <= 1'b0;
            memory_load_o  <= 1'b0;
        end else begin
            memory_shift_o <= 1'b0;
            memory_load_o  <= 1'b0;
        
            if (!spi_cs_sync && spi_sclk_falling) begin
                // Read the command
                spi_cmd <= {spi_cmd[6:0], spi_mosi_sync};
                spi_cnt <= spi_cnt + 1;
                
                if (spi_cnt == 7) begin
                    if (mode_i == 0) begin
                        // Read the command
                        user <= {spi_cmd[4:0], spi_mosi_sync};
                    end else begin
                        memory_shift_o <= 1'b1;
                        memory_load_o  <= 1'b1;
                    end
                end
            end
            
            // Echo back the previous values
            if (!spi_cs_sync && spi_sclk_rising) begin
                spi_miso_o <= spi_cmd[7];
            end
        end
    end

    // Assignments
    assign user_o = user;
    assign memory_instr_o = spi_cmd;

endmodule
