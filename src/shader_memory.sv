// SPDX-FileCopyrightText: © 2024 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module shader_memory #(
    parameter NUM_INSTR = 8
)(
    input  logic        clk_i,
    input  logic        rst_ni,
    input  logic        shift_i,
    output logic [7:0]  instr_o
);
    logic [7:0] memory [NUM_INSTR];
    int i;

    // Initialize the memory and shift the memory
    // by a whole word if shift_i is high
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            `ifdef COCOTB_SIM
            $readmemb("../sw/binary/test2.bit", memory);
            `else
            // Load the default program
            memory[0] <= 8'b00_0100_00; // GETX R0
            memory[1] <= 8'b00_0101_01; // GETY R1
            memory[2] <= 8'b01_11_01_00; // XOR R0 R1
            memory[3] <= 8'b00_0000_00; // SETRGB R0
            memory[4] <= 8'b01_11_00_00; // XOR R0 R0
            memory[5] <= 8'b01_11_00_00; // XOR R0 R0
            memory[6] <= 8'b01_11_00_00; // XOR R0 R0
            memory[7] <= 8'b01_11_00_00; // XOR R0 R0
            `endif
        end else begin
            if (shift_i) begin
                for (i=0; i<NUM_INSTR; i++) begin
                    if (i < NUM_INSTR-1) begin
                        memory[i] <= memory[i+1];
                    end else begin
                        memory[i] <= memory[0];
                    end
                end
            end
        end
    end
    
    assign instr_o = memory[0];

endmodule
