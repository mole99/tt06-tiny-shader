// SPDX-FileCopyrightText: © 2024 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module tiny_shader_top (
    input  logic        clk_i,
    input  logic        rst_ni,
    
    // SPI signals
    input  logic spi_sclk_i,
    input  logic spi_mosi_i,
    output logic spi_miso_o,
    input  logic spi_cs_i,
    
    // Mode signal
    // '0' = command mode
    // '1' = data mode
    input  logic mode_i,
    
    // SVGA signals
    output logic [5:0]  rrggbb_o,
    output logic        hsync_o,
    output logic        vsync_o,
    output logic        next_vertical_o,
    output logic        next_frame_o
);

    /*
        VGA 640x480 @ 60 Hz
        clock = 25.175 MHz
    */

    localparam WIDTH    = 640;
    localparam HEIGHT   = 480;
    
    localparam HFRONT   = 16;
    localparam HSYNC    = 96;
    localparam HBACK    = 48;

    localparam VFRONT   = 10;
    localparam VSYNC    = 2;
    localparam VBACK    = 33;
    
    localparam HTOTAL = WIDTH + HFRONT + HSYNC + HBACK;
    localparam VTOTAL = HEIGHT + VFRONT + VSYNC + VBACK;
    
    // Downscaling by factor of 8, i.e. one pixel is 8x8
    localparam WIDTH_SMALL  = WIDTH / 8; // 80
    localparam HEIGHT_SMALL = HEIGHT / 8; // 60

    /*
        Horizontal and Vertical Timing
    */
    
    logic signed [$clog2(HTOTAL) : 0] counter_h;
    logic signed [$clog2(VTOTAL) : 0] counter_v;
    
    logic hblank;
    logic vblank;
     
    // Horizontal timing
    timing #(
        .RESOLUTION     (WIDTH),
        .FRONT_PORCH    (HFRONT),
        .SYNC_PULSE     (HSYNC),
        .BACK_PORCH     (HBACK),
        .TOTAL          (HTOTAL),
        .POLARITY       (1)
    ) timing_hor (
        .clk        (clk_i),
        .enable     (1'b1),
        .reset_n    (rst_ni),
        .inc_1_or_4 (1'b0),
        .sync       (hsync_o),
        .blank      (hblank),
        .next       (next_vertical_o),
        .counter    (counter_h)
    );
    
    // Vertical timing
    timing #(
        .RESOLUTION     (HEIGHT),
        .FRONT_PORCH    (VFRONT),
        .SYNC_PULSE     (VSYNC),
        .BACK_PORCH     (VBACK),
        .TOTAL          (VTOTAL),
        .POLARITY       (1)
    ) timing_ver (
        .clk        (clk_i),
        .enable     (next_vertical_o),
        .reset_n    (rst_ni),
        .inc_1_or_4 (1'b0),
        .sync       (vsync_o),
        .blank      (vblank),
        .next       (next_frame_o),
        .counter    (counter_v)
    );
    
    logic [7:0] cur_time;
    logic time_dir;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            cur_time <= '0;
            time_dir <= '0;
        end else begin
            if (next_frame_o) begin
                if (time_dir == 1'b0) begin
                    cur_time <= cur_time + 1;
                    if (cur_time == 255-1) begin
                        time_dir <= 1'b1;
                    end
                end else begin
                    cur_time <= cur_time - 1;
                    if (cur_time == 0+1) begin
                        time_dir <= 1'b0;
                    end
                end
            end
        end
    end

    /*
        Final Color Composition
    */

    always_comb begin
        rrggbb_o = rgb_o;
        
        /*if (counter_v == 32) begin
            rrggbb_o = 6'b001100;
        end
        
        if (counter_h == 32) begin
            rrggbb_o = 6'b110000;
        end*/
        
        if (hblank || vblank) begin
            rrggbb_o = '0;
        end
    end


    /*
        SPI Receiver
        
        cpol       = False,
        cpha       = True,
        msb_first  = True,
        word_width = 8,
        cs_active_low = True
    */
    
    logic [7:0] memory_instr;
    logic memory_shift;
    logic memory_load;
    
    localparam NUM_REGS = 4;
    localparam REG_SIZE = 8;
    
    // TODO
    logic [NUM_REGS*REG_SIZE-1:0] registers;
    
    logic [7:0] reg0, reg1, reg2, reg3;
    
    assign reg0 = registers[0*8 +: 8];
    assign reg1 = registers[1*8 +: 8];
    assign reg2 = registers[2*8 +: 8];
    assign reg3 = registers[3*8 +: 8];
    
    spi_receiver #(
        .NUM_REGS       (NUM_REGS),
        .REG_SIZE       (REG_SIZE),
        .REG_DEFAULTS   ({NUM_REGS{8'b0}})
    ) spi_receiver_inst (
        .clk_i          (clk_i),
        .rst_ni         (rst_ni),
        
        // SPI signals
        .spi_sclk_i     (spi_sclk_i),
        .spi_mosi_i     (spi_mosi_i),
        .spi_miso_o     (spi_miso_o),
        .spi_cs_i       (spi_cs_i),
        
        // Mode signal
        .mode_i         (mode_i),
        
        .memory_instr_i (instr),
        .memory_instr_o (memory_instr),
        .memory_shift_o (memory_shift),
        .memory_load_o  (memory_load),
        
        // Output registers
        .registers_o (registers)
    );

    // Graphics

    logic [5:0] counter_h_small;
    logic [5:0] counter_v_small;
    
    assign counter_h_small = counter_h[$clog2(HTOTAL)-2 : 3];
    assign counter_v_small = counter_v[$clog2(HTOTAL)-2 : 3];

    logic [7:0] instr;

    logic execute_shader;
    assign execute_shader = counter_h+8 >= 0 && counter_h+8 < WIDTH 
                            && counter_v >= 0 && counter_v < HEIGHT;

    shader_memory shader_memory_inst (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .shift_i    (execute_shader || memory_shift),
        .load_i     (memory_load),
        .instr_i    (memory_instr),
        .instr_o    (instr)
    );

    logic [5:0] x_pos;
    logic [5:0] y_pos;
    logic [2:0] substep;
    
    logic [5:0] rgb_o;
    logic [5:0] rgb_d;

    shader_execute shader_execute_inst (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .instr_i    (instr),
        .execute    (execute_shader),
        
        .x_pos_i    (counter_h_small+6'd1),// +1
        .y_pos_i    (counter_v_small),
        
        .rgb_o      (rgb_o)
    );

endmodule
