// SPDX-FileCopyrightText: © 2024 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module tiny_shader_top (
    input  logic        clk_i,
    input  logic        rst_ni,
    
    // SPI signals
    // TODO
    
    // SVGA signals
    output logic [5:0] rrggbb_o,
    output logic hsync_o,
    output logic vsync_o,
    output logic next_vertical_o,
    output logic next_frame_o
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
    
    // TODO

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
        .shift_i    (execute_shader),
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
