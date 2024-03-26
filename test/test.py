# SPDX-FileCopyrightText: © 2024 Leo Moser <leomoser99@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from PIL import Image, ImageChops

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import Timer, RisingEdge, FallingEdge

# VGA Parameters
WIDTH    = 640;
HEIGHT   = 480;

HFRONT   = 16;
HSYNC    = 96;
HBACK    = 48;

VFRONT   = 10;
VSYNC    = 2;
VBACK    = 33;

# Reset coroutine
async def reset_dut(rst_ni, duration_ns):
    rst_ni.value = 0
    await Timer(duration_ns, units="ns")
    rst_ni.value = 1
    rst_ni._log.debug("Reset complete")

# Draw the current frame and return it
async def draw_frame(dut):
    screen_x = -HBACK
    screen_y = -VBACK

    #print(dut.timing_hor.counter.value.integer)
    #print(dut.timing_ver.counter.value.integer)
    print(f"line {screen_y}")

    image = Image.new('RGB', (WIDTH, HEIGHT), "black")
    pixels = image.load()

    while (1):
        await RisingEdge(dut.clk)
    
        # Expand color data
        r = dut.rrggbb.value[0:1] << 6
        if (r & 1<<6):
            r = r | 0x3F
        g = dut.rrggbb.value[2:3] << 6
        if (g & 1<<6):
            g = g | 0x3F
        b = dut.rrggbb.value[4:5] << 6
        if (b & 1<<6):
            b = b | 0x3F

        # Inside drawing area
        if screen_y >= 0 and screen_y < HEIGHT and screen_x >= 0 and screen_x < WIDTH:
            #print(dut.timing_hor.counter.value.integer)
            #print(dut.timing_ver.counter.value.integer)
            pixels[screen_x, screen_y] = (r, g, b)
        
        # Received hsync
        if (dut.hsync.value == 1):
            await FallingEdge(dut.hsync)
            screen_y += 1
            #print(dut.timing_hor.counter.value.integer)
            #print(dut.timing_ver.counter.value.integer)
            print(f"line {screen_y}")
            screen_x = -HBACK

        # Received vsync
        elif (dut.vsync.value == 1):
            await FallingEdge(dut.vsync)
            await FallingEdge(dut.hsync)
            return image
        else:
            screen_x += 1

@cocotb.test()
async def test_vga(dut):
    dut._log.info("Starting test_vga")

    # Start the clock
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())

    # Assign default values

    # Reset
    await reset_dut(dut.rst_n, 50)
    dut._log.info("Reset done")
    
    await FallingEdge(dut.vsync)
    await FallingEdge(dut.hsync)
    
    # Start thread to draw frame
    taks_draw_frame = await cocotb.start(draw_frame(dut))

    # Set the input values, wait one clock cycle, and check the output
    dut._log.info("Test")

    image = await taks_draw_frame.join()
    image.save(f"test1.png")

    await ClockCycles(dut.clk, 10)
