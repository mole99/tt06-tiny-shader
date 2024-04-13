// SPDX-FileCopyrightText: © 2024 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module shader_execute (
    input  logic        clk_i,
    input  logic        rst_ni,
    input  logic [7:0]  instr_i,
    input  logic        execute,
    
    input logic  [5:0]  x_pos_i,
    input logic  [5:0]  y_pos_i,
    
    output logic [5:0]  rgb_o
);

    localparam NUM_REGS = 4;

    logic [5:0] regs [NUM_REGS];

    int i;
    
    // Decode stage
    
    logic dual_arg; // Is this a dual argument instruction?
    assign dual_arg = instr_i[7];
    
    logic [1:0] arg0;
    logic [1:0] arg1; // valid if dual_arg
    
    assign arg0 = instr_i[1:0];
    assign arg1 = instr_i[3:2];
    
    logic [5:0] imm; // immediate value
    assign imm = instr_i[5:0];


    // TODO
    logic [5:0] sine_lut [16];

    logic [5:0] rgb;
    logic [5:0] cur_time;
    logic [5:0] user;
    logic skip;

    always_ff @(posedge clk_i) begin
        if (!rst_ni) begin
            for (i=0; i<NUM_REGS; i++) begin
                regs[i] <= '0;
            end
            
            sine_lut[0] <= 6'd0;
            sine_lut[1] <= 6'd6;
            sine_lut[2] <= 6'd13;
            sine_lut[3] <= 6'd19;
            sine_lut[4] <= 6'd25;
            sine_lut[5] <= 6'd31;
            sine_lut[6] <= 6'd37;
            sine_lut[7] <= 6'd42;
            sine_lut[8] <= 6'd46;
            sine_lut[9] <= 6'd50;
            sine_lut[10] <= 6'd54;
            sine_lut[11] <= 6'd57;
            sine_lut[12] <= 6'd59;
            sine_lut[13] <= 6'd61;
            sine_lut[14] <= 6'd62;
            sine_lut[15] <= 6'd63;

            
            rgb      <= 6'b000000;
            cur_time <= 5;
            user     <= 42;
            skip     <= 1'b0;

        end else begin
            if (execute) begin
                if (skip) begin
                    skip <= 1'b0;
                end else begin
            
                    casez (instr_i)
                    
                        // Single arg instructions
                        8'b00_0000_??: begin //  SETRGB RGB <= ARG0[1:0]
                            rgb <= regs[arg0]; // TODO nop
                        end
                        8'b00_0001_??: begin //  SETR R <= ARG0[1:0]
                            rgb[5:4] <= regs[arg0][1:0];
                        end
                        8'b00_0010_??: begin //  SETG G <= ARG0[1:0]
                            rgb[3:2] <= regs[arg0][1:0];
                        end
                        8'b00_0011_??: begin //  SETB B <= ARG0[1:0]
                            rgb[1:0] <= regs[arg0][1:0];
                        end
                        
                        8'b00_0100_??: begin //  GETX ARG0 <= X
                            regs[arg0] <= x_pos_i;
                        end
                        8'b00_0101_??: begin //  GETY ARG0 <= Y
                            regs[arg0] <= y_pos_i;
                        end
                        8'b00_0110_??: begin //  GETTIME ARG0 <= TIME
                            regs[arg0] <= cur_time;
                        end
                        8'b00_0111_??: begin //  GETUSER ARG0 <= USER
                            regs[arg0] <= user;
                        end

                        8'b00_1000_??: begin //  IF ARG0 == REGS[0]
                            skip <= !(regs[arg0] == regs[0]);
                        end
                        8'b00_1001_??: begin //  IF ARG0 != REGS[0]
                            skip <= !(regs[arg0] != regs[0]);
                        end
                        8'b00_1010_??: begin //  IF ARG0 >= REGS[0]
                            skip <= !(regs[arg0] >= regs[0]);
                        end
                        8'b00_1011_??: begin // IF ARG0 < REGS[0]
                            skip <= !(regs[arg0] < regs[0]);
                        end

                        8'b00_1100_??: begin // TODO special RGB to set all channels same, or use high bits from operand

                        end
                        8'b00_1101_??: begin // TODO duplicate

                        end
                        8'b00_1110_??: begin // TODO half

                        end
                        8'b00_1111_??: begin // SINE ARG0 <= SINE_LUT[REGS[0]]
                            regs[arg0] <= sine_lut[regs[0][5:2]]; // TODO
                        end
                        
                        
                        // Dual arg instructions 01 - Logical
                        8'b01_00_??_??: begin // AND ARG0 <= ARG0 & ARG1
                            regs[arg0] <= regs[arg0] & regs[arg1];
                        end
                        8'b01_01_??_??: begin // OR ARG0 <= ARG0 | ARG1
                            regs[arg0] <= regs[arg0] | regs[arg1];
                        end
                        8'b01_10_??_??: begin // NOT ARG0 <= ~ARG1
                            regs[arg0] <= ~regs[arg1];
                        end
                        8'b01_11_??_??: begin // XOR ARG0 <= ARG0 ^ ARG1 
                            regs[arg0] <= regs[arg0] ^ regs[arg1];
                        end
                        
                        // Dual arg instructions 10
                        8'b10_00_??_??: begin // MOV ARG0 <= ARG1
                            regs[arg0] <= regs[arg1];
                        end
                        8'b10_01_??_??: begin // ADD ARG0 <= ARG0 + ARG1
                            regs[arg0] <= regs[arg0] + regs[arg1];
                        end
                        8'b10_10_??_??: begin // SHIFTL ARG0 <= ARG0 << ARG1
                            regs[arg0] <= regs[arg0] << regs[arg1];
                        end
                        8'b10_11_??_??: begin // SHIFTR ARG0 <= ARG0 >> ARG1
                            regs[arg0] <= regs[arg0] >> regs[arg1];
                        end
                        
                        // Load immediate 11
                        8'b11_??????: begin // LDI REGS[0] <= IMM
                            regs[0] <= imm;
                        end

                    
                        default: begin
                        
                        end
                    endcase
                end
            end
        end
    end
    
    assign rgb_o = rgb;

endmodule
