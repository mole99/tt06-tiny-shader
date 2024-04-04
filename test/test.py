# SPDX-FileCopyrightText: © 2024 Leo Moser <leomoser99@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import os
import random
from PIL import Image, ImageChops
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import Timer, RisingEdge, FallingEdge

from cocotbext.spi import SpiBus, SpiConfig, SpiMaster

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

# Send cmd and payload over SPI
async def spi_send_cmd(dut, spi_master, cmd, data, burst=False):
    print(f'CMD: {cmd} DATA: {data}')
    await spi_master.write(cmd)
    await spi_master.write(data, burst=burst)

@cocotb.test()
async def test_vga_default(dut):
    dut._log.info("Starting test_vga")

    # Start the clock
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())

    # Assign default values
    dut.ena.value = 1
    dut.mode.value = 0 # cmd mode

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
    image.save(f"default.png")

    await ClockCycles(dut.clk, 10)

@cocotb.test(skip=os.environ.get('GL_TEST', None) != None)
async def test_spi_regs(dut):

    # Start the clock
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    
    spi_bus = SpiBus.from_prefix(dut, "spi")

    spi_config = SpiConfig(
        word_width = 8,
        sclk_freq  = 2e6,
        cpol       = False,
        cpha       = True,
        msb_first  = True,
        frame_spacing_ns = 500
    )

    spi_master = SpiMaster(spi_bus, spi_config)

    # Assign default values
    dut.ena.value = 1
    dut.mode.value = 0 # cmd mode

    # Reset
    await reset_dut(dut.rst_n, 50)
    dut._log.info("Reset done")
    
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == 0x00)
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg1.value == 0x00)
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg2.value == 0x00)
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg3.value == 0x00)
    
    # Set reg0
    await spi_send_cmd(dut, spi_master, [0x0], [0x03])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == 0x03)
    
    # Set reg1
    await spi_send_cmd(dut, spi_master, [0x1], [0x70])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg1.value == 0x70)
    
    # Set reg2
    await spi_send_cmd(dut, spi_master, [0x2], [0xEA])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg2.value == 0xEA)
    
    # Set reg3
    await spi_send_cmd(dut, spi_master, [0x3], [0xF3])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg3.value == 0xF3)

    # Set reg0
    await spi_send_cmd(dut, spi_master, [0x0], [0x42])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == 0x42)

    await ClockCycles(dut.clk, 10)

@cocotb.test(skip=os.environ.get('GL_TEST', None) != None)
async def test_spi_shader(dut):

    # Start the clock
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    
    spi_bus = SpiBus.from_prefix(dut, "spi")

    spi_config = SpiConfig(
        word_width = 8,
        sclk_freq  = 2e6,
        cpol       = False,
        cpha       = True,
        msb_first  = True,
        frame_spacing_ns = 500
    )

    spi_master = SpiMaster(spi_bus, spi_config)

    # Assign default values
    dut.ena.value = 1
    dut.mode.value = 1 # data mode

    # Reset
    await reset_dut(dut.rst_n, 50)
    dut._log.info("Reset done")
    
    # Send shader instructions
    shader = [0x12, 0x00, 0xFF, 0x64, 0x42, 0x11, 0x97, 0x0F]
    await spi_master.write(shader, burst=True)

    # Verify shader was correctly written
    for i in range(8):
        assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.shader_memory_inst.memory[i].value == shader[i])

    await ClockCycles(dut.clk, 10)
    
@cocotb.test(skip=os.environ.get('GL_TEST', None) != None)
async def test_spi_regs_shader_regs_random(dut):

    # Start the clock
    c = Clock(dut.clk, 10, 'ns')
    await cocotb.start(c.start())
    
    spi_bus = SpiBus.from_prefix(dut, "spi")

    spi_config = SpiConfig(
        word_width = 8,
        sclk_freq  = 2e6,
        cpol       = False,
        cpha       = True,
        msb_first  = True,
        frame_spacing_ns = 500
    )

    spi_master = SpiMaster(spi_bus, spi_config)

    # Assign default values
    dut.ena.value = 1
    dut.mode.value = 0 # cmd mode

    # Reset
    await reset_dut(dut.rst_n, 50)
    dut._log.info("Reset done")
    
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == 0x00)
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg1.value == 0x00)
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg2.value == 0x00)
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg3.value == 0x00)
    
    # Set reg0
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x0], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == data)
    
    # Set reg1
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x1], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg1.value == data)
    
    # Set reg2
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x2], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg2.value == data)
    
    # Set reg3
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x3], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg3.value == data)

    # Set reg0
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x0], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == data)

    dut.mode.value = 1 # data mode
    
    # Send shader instructions
    shader = [random.randint(0, 255) for i in range(8)]
    await spi_master.write(shader, burst=True)

    # Verify shader was correctly written
    for i in range(8):
        assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.shader_memory_inst.memory[i].value == shader[i])

    await ClockCycles(dut.clk, 10)
    
    dut.mode.value = 0 # cmd mode
    
    # Set reg0
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x0], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == data)
    
    # Set reg1
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x1], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg1.value == data)
    
    # Set reg2
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x2], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg2.value == data)
    
    # Set reg3
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x3], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg3.value == data)

    # Set reg0
    data = random.randint(0, 255)
    await spi_send_cmd(dut, spi_master, [0x0], [data])
    assert(dut.tt_um_tiny_shader_mole99_inst.tiny_shader_top_inst.reg0.value == data)
