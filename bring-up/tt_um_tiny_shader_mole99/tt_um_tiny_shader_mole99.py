import time
import sys
import gc
import random
from machine import Pin
from machine import SoftSPI
from .pio_spi import PIOSPI
from ttboard.demoboard import DemoBoard, Pins

def send_cmd(tt, spi, cmd):
    tt.ui_in[0] = 0 # cmd mode (user reg)
    tt.uio_in[0] = 0 # start
    spi.write(cmd)
    tt.uio_in[0] = 1 # stop

def send_data(tt, spi, data):
    tt.ui_in[0] = 1 # data mode (shader data)
    tt.uio_in[0] = 0 # start
    spi.write(data)
    tt.uio_in[0] = 1 # stop

shader_test1 = bytes([
    0b00111000, # CLEAR R0
    0b00000000, # SETRGB R0
    0b00010001, # GETX R1
    0b00010110, # GETY R2
    0b00011000, # GETTIME R0
    0b00100001, # IFEQ R1
    0b00000001, # SETRGB R1
    0b00100010, # IFEQ R2
    0b00000010, # SETRGB R2
    0b01000000, # NOP
])

shader_test2 = bytes([
    0b00011010, # GETTIME R2
    0b00010000, # GETX R0
    0b10011000, # ADD R0 R2
    0b00111101, # SINE R1
    0b00000101, # SETR R1
    0b00010100, # GETY R0
    0b10011000, # ADD R0 R2
    0b00111101, # SINE R1
    0b00001001, # SETG R1
    0b01000000, # NOP
])

shader_test3 = bytes([
    0b00010000, # GETX R0
    0b00000100, # SETR R0
    0b00010101, # GETY R1
    0b00001001, # SETG R1
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
])

shader_test4 = bytes([
    0b00010000, # GETX R0
    0b00010101, # GETY R1
    0b01110100, # XOR R0 R1
    0b00011010, # GETTIME R2
    0b10011000, # ADD R0 R2
    0b00000000, # SETRGB R0
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
])

shader_test5 = bytes([
    0b00010101, # GETY R1
    0b11000001, # LDI 1
    0b01000001, # AND R1 R0
    0b00100101, # IFNE R1
    0b11111111, # LDI 63
    0b00100001, # IFEQ R1
    0b11000000, # LDI 0
    0b00000000, # SETRGB R0
    0b01000000, # NOP
    0b01000000, # NOP
])

shader_test6 = bytes([
    0b00010001, # GETX R1
    0b11000001, # LDI 1
    0b01000001, # AND R1 R0
    0b00100101, # IFNE R1
    0b11111111, # LDI 63
    0b00100001, # IFEQ R1
    0b11000000, # LDI 0
    0b00000000, # SETRGB R0
    0b01000000, # NOP
    0b01000000, # NOP
])

shader_test7 = bytes([
    0b00111011, # CLEAR R3
    0b00010000, # GETX R0
    0b00011001, # GETTIME R1
    0b10010100, # ADD R0 R1
    0b00000000, # SETRGB R0
    0b00111100, # SINE R0
    0b00110100, # HALF R0
    0b00010101, # GETY R1
    0b00101001, # IFGE R1
    0b00000011, # SETRGB R3
])

shader_test8 = bytes([
    0b00111011, # CLEAR R3
    0b00010100, # GETY R0
    0b00011001, # GETTIME R1
    0b10010100, # ADD R0 R1
    0b00000000, # SETRGB R0
    0b00111100, # SINE R0
    0b00110100, # HALF R0
    0b00010001, # GETX R1
    0b00101001, # IFGE R1
    0b00000011, # SETRGB R3
])

shader_test9 = bytes([
    0b00010000, # GETX R0
    0b00111110, # SINE R2
    0b00010100, # GETY R0
    0b00111100, # SINE R0
    0b10011000, # ADD R0 R2
    0b00011001, # GETTIME R1
    0b10010100, # ADD R0 R1
    0b00011101, # GETUSER R1
    0b10010100, # ADD R0 R1
    0b00000000, # SETRGB R0
])

shader_test10 = bytes([
    0b00010000, # GETX R0
    0b00011001, # GETTIME R1
    0b10010100, # ADD R0 R1
    0b00111110, # SINE R2
    0b00010100, # GETY R0
    0b00011001, # GETTIME R1
    0b10010100, # ADD R0 R1
    0b00111100, # SINE R0
    0b10011000, # ADD R0 R2
    0b00000000, # SETRGB R0
])

shader_test11 = bytes([
    0b00110000, # DOUBLE R0
    0b00000000, # SETRGB R0
    0b00111011, # CLEAR R3
    0b00100011, # IFEQ R3
    0b00011000, # GETTIME R0
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
])

shader_test12 = bytes([
    0b00010000, # GETX R0
    0b00111101, # SINE R1
    0b00010100, # GETY R0
    0b00111100, # SINE R0
    0b01110100, # XOR R0 R1
    0b00011001, # GETTIME R1
    0b10010100, # ADD R0 R1
    0b00000000, # SETRGB R0
    0b01000000, # NOP
    0b01000000, # NOP
])

shaders = [
    shader_test1,
    shader_test2,
    shader_test3,
    shader_test4,
    shader_test5,
    shader_test6,
    shader_test7,
    shader_test8,
    shader_test9,
    shader_test10,
    shader_test11,
    shader_test12,
]

shaders_slideshow = [
    shader_test9,
    shader_test2,
    shader_test1,
    shader_test4,
    shader_test8,
    shader_test5,
    shader_test10,
    shader_test12,
]

def load_shader_manual_clock(tt, shader):
    print('Loading new shader')

    # Stop automatic clock
    tt.clock_project_stop()
    
    print('Clock stopped')

    tt.reset_project(True)
    tt.clk.mode = Pin.OUT
    
    for i in range(2):
        tt.clk(0)
        time.sleep_us(1)
        tt.clk(1)
    
    tt.reset_project(False)
    
    print('Shader reset')
    
    # CS - chip select, active low
    tt.pins.pin_uio0.init(Pin.OUT) # output
    tt.pins.pin_uio0.value(1) # high
    
    # MOSI
    tt.pins.pin_uio1.init(Pin.OUT) # output
    tt.pins.pin_uio1.value(0) # low
    
    # SCK
    tt.pins.pin_uio3.init(Pin.OUT) # output
    tt.pins.pin_uio3.value(1) # high
    
    tt.pins.pin_ui_in0.value(1) # data mode (shader data)
    
    for byte in shader:

        tt.pins.pin_uio0.value(0) # CS start
    
        tt.pins.rp_projclk.value(0)
        time.sleep_us(1)
        tt.pins.rp_projclk.value(1)
    
        for bit_pos in reversed(range(8)):
            bit = (byte & (1<<bit_pos))>>bit_pos
            #print(bit, end='')
            
            tt.pins.pin_uio1.value(bit) # MOSI
            
            tt.pins.pin_uio3.value(1) # SCK High
            
            tt.pins.rp_projclk.value(0)
            time.sleep_us(1)
            tt.pins.rp_projclk.value(1)

            tt.pins.pin_uio3.value(0) # SCK Low
            
            tt.pins.rp_projclk.value(0)
            time.sleep_us(1)
            tt.pins.rp_projclk.value(1)
            
        #print('')

        tt.pins.pin_uio0.value(1) # CS stop
        
        tt.pins.rp_projclk.value(0)
        time.sleep_us(1)
        tt.pins.rp_projclk.value(1)
    
    # activate automatic clock
    tt.clock_project_PWM(25175000)

    print('Shader upload complete')

def load_project(tt:DemoBoard):
    
    if not tt.shuttle.has('tt_um_tiny_shader_mole99'):
        print("No tt_um_tiny_shader_mole99 available in shuttle?")
        return False
    
    tt.shuttle.tt_um_tiny_shader_mole99.enable()
    return True

def select_shader(tt, index):
    if 0 <= index < len(shaders):
        load_shader_manual_clock(tt, shaders[index])
    else:
        print(f'Invalid shader index: {index}')
        print(f'Max index: {len(shaders)-1}')

def main():
    tt = DemoBoard.get()
    
    if not load_project(tt):
        return
    
    tt.uio_oe_pico.value = 0 # all inputs
    
    """tt.rst_n.mode = Pins.OUT
    tt.rst_n(0)
    time.sleep_ms(1000)
    tt.rst_n(1)"""
    
    while 1:
        print('Please input shader index or action ("user", "count", "slideshow", "random"): ')
        
        input = sys.stdin.readline().rstrip()
        print(f'"{input}"')

        if input == 'user':
            print('Please input user number (0-63): ')
            
            input = sys.stdin.readline().rstrip()
            print(input)
            
            user = int(input)
            spi = PIOSPI(sm_id=0, pin_mosi=tt.pins.pin_uio1, pin_miso=tt.pins.pin_uio2, pin_sck=tt.pins.pin_uio3, cpha=True, cpol=False, freq=int(5e6))
            send_cmd(tt, spi, user.to_bytes(1, sys.byteorder))
        elif input == 'count':
            spi = PIOSPI(sm_id=0, pin_mosi=tt.pins.pin_uio1, pin_miso=tt.pins.pin_uio2, pin_sck=tt.pins.pin_uio3, cpha=True, cpol=False, freq=int(5e6))
        
            for i in range(64):
                send_cmd(tt, spi, i.to_bytes(1, sys.byteorder))
                time.sleep_ms(16)
        elif input == 'slideshow':
            for shader in shaders_slideshow:
                load_shader_manual_clock(tt, shader)
                time.sleep(6)
        elif input == 'random':
            for i in range(10):
                index = random.randint(0, len(shaders)-1)
                load_shader_manual_clock(tt, shaders[index])
                time.sleep(5)
        else:
            try:
                select_shader(tt, int(input))
            except:
                print('Invalid input.')
"""
>>> import examples.tt_um_tiny_shader_mole99 as test
>>> test.run()
"""
