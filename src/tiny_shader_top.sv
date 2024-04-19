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
    output logic [5:0] rrggbb_o,
    output logic       hsync_o,
    output logic       vsync_o,
    output logic       next_vertical_o,
    output logic       next_frame_o
);

    /* Tiny Shader Settings */
    
    localparam NUM_INSTR = 10;

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

    /* Horizontal and Vertical Timing */
    
    logic signed [$clog2(HTOTAL) : 0] counter_h;
    logic signed [$clog2(VTOTAL) : 0] counter_v;
    
    logic hblank;
    logic vblank;
    logic hsync;
    logic vsync;
    logic next_vertical;
    logic next_frame;
     
    // Horizontal timing
    timing #(
        .RESOLUTION     (WIDTH),
        .FRONT_PORCH    (HFRONT),
        .SYNC_PULSE     (HSYNC),
        .BACK_PORCH     (HBACK),
        .TOTAL          (HTOTAL),
        .POLARITY       (1'b0)
    ) timing_hor (
        .clk        (clk_i),
        .enable     (1'b1),
        .reset_n    (rst_ni),
        .inc_1_or_4 (1'b0),
        .sync       (hsync),
        .blank      (hblank),
        .next       (next_vertical),
        .counter    (counter_h)
    );

    // Vertical timing
    timing #(
        .RESOLUTION     (HEIGHT),
        .FRONT_PORCH    (VFRONT),
        .SYNC_PULSE     (VSYNC),
        .BACK_PORCH     (VBACK),
        .TOTAL          (VTOTAL),
        .POLARITY       (1'b0)
    ) timing_ver (
        .clk        (clk_i),
        .enable     (next_vertical),
        .reset_n    (rst_ni),
        .inc_1_or_4 (1'b0),
        .sync       (vsync),
        .blank      (vblank),
        .next       (next_frame),
        .counter    (counter_v)
    );
    
    logic [8:0] cur_time;
    logic time_dir;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            cur_time <= '0;
            time_dir <= '0;
        end else begin
            if (next_frame) begin
                if (time_dir == 1'b0) begin
                    cur_time <= cur_time + 1;
                    if (&(cur_time+1)) begin
                        time_dir <= 1'b1;
                    end
                end else begin
                    cur_time <= cur_time - 1;
                    if (cur_time == 1) begin
                        time_dir <= 1'b0;
                    end
                end
            end
        end
    end

    /* SPI Receiver
        
        cpol       = False,
        cpha       = True,
        msb_first  = True,
        word_width = 8,
        cs_active_low = True
    */
    
    logic [7:0] memory_instr;
    logic memory_shift;
    logic memory_load;
    
    logic [5:0] user;
    
    spi_receiver #(
        .REG_SIZE       (6),
        .REG_DEFAULT    (6'd42)
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

        // Output memory
        .memory_instr_o (memory_instr),
        .memory_shift_o (memory_shift),
        .memory_load_o  (memory_load),
        
        // Output register
        .user_o (user)
    );

    // Graphics

    logic [7:0] instr;

    logic execute_shader_x, execute_shader_y;
    assign execute_shader_x = counter_h+NUM_INSTR >= 0 && counter_h+NUM_INSTR < WIDTH 
                            && counter_v >= 0 && counter_v < HEIGHT;
                            
    assign execute_shader_y = counter_v >= 0 && counter_v < HEIGHT;            

                            
    /* Shader Memory */

    shader_memory #(
        .NUM_INSTR (NUM_INSTR)
    ) shader_memory_inst (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .shift_i    (execute_shader_x || x_subpos > 0 || memory_shift),
        .load_i     (memory_load),
        .instr_i    (memory_instr),
        .instr_o    (instr)
    );
    
    /* Count subpixel positions */

    logic [$clog2(NUM_INSTR) - 1:0] x_subpos;
    logic [$clog2(NUM_INSTR) - 1:0] y_subpos;
    
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            x_subpos <= '0;
            y_subpos <= '0;
        end else begin
            if (execute_shader_x || x_subpos > 0) begin
                // X sub position
                x_subpos <= x_subpos + 1;
                
                if (x_subpos == NUM_INSTR-1) begin
                    x_subpos <= '0;
                end
            end
            
            if (execute_shader_y) begin
            
                // Y sub position
                if (next_vertical) begin
                    y_subpos <= y_subpos + 1;
                    
                    if (y_subpos == NUM_INSTR-1) begin
                        y_subpos <= '0;
                    end
                end
            
            end
        end
    end
    
    /* Count x and y positions */

    localparam WIDTH_SMALL = WIDTH / NUM_INSTR;
    localparam HEIGHT_SMALL = HEIGHT / NUM_INSTR;
    
    logic [$clog2(WIDTH_SMALL)  - 1:0] x_pos;
    logic [$clog2(HEIGHT_SMALL) - 1:0] y_pos;
    
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            x_pos <= '0;
            y_pos <= '0;
        end else begin
            if (x_subpos == NUM_INSTR-1) begin
                x_pos <= x_pos + 1;
            end

            if (next_vertical) begin
                x_pos <= '0;

                if (y_subpos == NUM_INSTR-1) begin
                    y_pos <= y_pos + 1;
                end
            end

            if (next_frame) begin
                y_pos <= '0;
            end
        end
    end
    
    /* Shader execution */
    
    logic [5:0] rgb_o;
    logic [5:0] rgb_d;

    shader_execute shader_execute_inst (
        .clk_i      (clk_i),
        .rst_ni     (rst_ni),
        .instr_i    (instr),
        .execute    (execute_shader_x),
        
        .x_pos_i    (x_pos),
        .y_pos_i    (y_pos),
        
        .time_i     (cur_time[8:3]),
        .user_i     (user),
        
        .rgb_o      (rgb_o)
    );

    // Capture output color, after shader completed
    
    logic capture;
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            capture <= '0;
            rgb_d <= '0;
        end else begin
            capture <= x_subpos == NUM_INSTR-1;

            if (capture) begin
                rgb_d <= rgb_o;
            end
            
            // Blanking intervall
            if (hblank || vblank) begin
                rgb_d <= '0;
            end
        end
    end
    
    assign rrggbb_o = rgb_d;
    
    // Delay output signals one cycle
    // to account for rgb_d
    always_ff @(posedge clk_i) begin
        hsync_o         <= hsync;
        vsync_o         <= vsync;
        next_vertical_o <= next_vertical;
        next_frame_o    <= next_frame;
    end


endmodule
