import time
import sys
import gc
from machine import Pin
from machine import SoftSPI
from .pio_spi import PIOSPI
from ttboard.demoboard import DemoBoard, Pins

frame_trig = False
def isr_frame(t):
    global frame_trig
    frame_trig = True

line_trig = False
def isr_line(t):
    global line_trig
    line_trig = True

def sync_frame():
    global frame_trig
    frame_trig = False
    while not frame_trig:
        pass

def sync_line():
    global line_trig
    line_trig = False
    while not line_trig:
        pass

def sync():
    sync_frame()

    for i in range(4):
        sync_line()

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
    0b11010000, # LDI 0x10
    0b00100001, # IFEQ R1
    0b00000001, # SETRGB R1
    0b00100010, # IFEQ R2
    0b00000010, # SETRGB R2
    0b01000000, # NOP
])

shader_test2 = bytes([
    0b00010000, # GETX R0
    0b00111101, # SINE R1
    0b00000101, # SETR R1
    0b00010100, # GETY R0
    0b00111101, # SINE R1
    0b00001001, # SETG R1
    0b01000000, # NOP
    0b01000000, # NOP
    0b01000000, # NOP
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
    0b00011101, # GETUSER R1
    0b10010100, # ADD R0 R1
    0b00000000, # SETRGB R0
    0b00111100, # SINE R0
    0b00110100, # HALF R0
    0b00010101, # GETY R1
    0b00101001, # IFGE R1
    0b00000011, # SETRGB R3
])

shader_test8 = bytes([
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

def shader_test(tt):
    # CS - chip select, active low
    tt.uio_oe_pico[0] = 1 # output
    tt.uio_in[0] = 1 # high
    
    spi = SoftSPI(baudrate=int(1e6), polarity=0, phase=1, bits=8, sck=tt.pins.pin_uio3, mosi=tt.pins.pin_uio1, miso=tt.pins.pin_uio2) #firstbit=MSB
    
    #spi = PIOSPI(sm_id=0, pin_mosi=tt.pins.pin_uio1, pin_miso=tt.pins.pin_uio2, pin_sck=tt.pins.pin_uio3, cpha=True, cpol=False, freq=int(5e6)) # freq=int(126000000//10))

    #tt.pins.pin_uio4.irq(trigger=Pin.IRQ_FALLING, handler=isr_line)
    #tt.pins.pin_uio5.irq(trigger=Pin.IRQ_FALLING, handler=isr_frame)

    # Use vsync, hsync
    tt.pins.pin_uo_out3.irq(trigger=Pin.IRQ_FALLING, handler=isr_frame)
    tt.pins.pin_uo_out7.irq(trigger=Pin.IRQ_FALLING, handler=isr_line)

    time.sleep_ms(4000)
    
    #for byte in shader_test1:
    #    sync()
    #    send_data(tt, spi, byte.to_bytes(1, sys.byteorder))
    #time.sleep_ms(6000)
    
    #sync()
    #sync_frame()
    #sync_line()
    #send_data(tt, spi, shader_test2)
    
    #input = sys.stdin.readline()
    
    """for i in range(50):
        #for byte in shader_test1:
        #    sync_frame()
        #    send_data(tt, spi, byte.to_bytes(1, sys.byteorder))
        #sync_frame()
        #time.sleep_ms(i)
        
        while tt.pins.pin_uo_out3.value() != 1:
            pass
        
        while tt.pins.pin_uo_out3.value() != 0:
            pass
        
        send_data(tt, spi, shader_test1)
        time.sleep_ms(1000)"""
    
    gc.disable()
    
    while 1:
        sync_frame()

        #while tt.pins.pin_uo_out3.value() != 1:
        #    pass
        
        #while tt.pins.pin_uo_out3.value() != 0:
        #    pass

        #tt.ui_in[3] = 1
        #tt.ui_in[3] = 0

        tt.pins.pin_ui_in3.value(1)
        tt.pins.pin_ui_in3.value(0)

        #send_data(tt, spi, shader_test1)
    
    gc.enable()
    
    #time.sleep_ms(6000)
    #send_cmd(tt, spi, b'\x00')


def load_shader_manual_clock(tt, shader):
    print('Loading new shader')

    # Stop automatic clock
    tt.clock_project_stop()
    
    print('Clock stopped')

    tt.reset_project(True)
    tt.clk.mode = Pin.OUT
    
    for i in range(3):
        tt.clk(0)
        time.sleep_ms(1)
        tt.clk(1)
    
    tt.reset_project(False)
    
    print('Shader reset')
    
    # CS - chip select, active low
    tt.uio_oe_pico[0] = 1 # output
    tt.uio_in[0] = 1 # high
    
    # MOSI
    tt.uio_oe_pico[1] = 1 # output
    tt.uio_in[1] = 0 # low
    
    # SCK
    tt.uio_oe_pico[3] = 1 # output
    tt.uio_in[3] = 1 # high
    
    tt.ui_in[0] = 1 # data mode (shader data)

    
    for byte in shader:
    
        tt.uio_in[0] = 0 # CS start
    
        for i in range(2):
            tt.clk(0)
            time.sleep_ms(1)
            tt.clk(1)
    
        for bit_pos in reversed(range(8)):
            bit = (byte & (1<<bit_pos))>>bit_pos
            print(bit, end='')
            
            tt.uio_in[1] = bit # MOSI
            
            tt.uio_in[3] = 1 # SCK High
            
            for i in range(2):
                tt.clk(0)
                time.sleep_ms(1)
                tt.clk(1)

            tt.uio_in[3] = 0 # SCK Low
            
            for i in range(2):
                tt.clk(0)
                time.sleep_ms(1)
                tt.clk(1)
            
        print('')

        tt.uio_in[0] = 1 # CS stop
        
        for i in range(2):
            tt.clk(0)
            time.sleep_ms(1)
            tt.clk(1)
    
    # activate automatic clock
    tt.clock_project_PWM(25175000)

    print('Shader upload complete')

def load_project(tt:DemoBoard):
    
    if not tt.shuttle.has('tt_um_tiny_shader_mole99'):
        print("No tt_um_tiny_shader_mole99 available in shuttle?")
        return False
    
    tt.shuttle.tt_um_tiny_shader_mole99.enable()
    return True

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
        print('Please input shader number or action (1-9, user, count): ')
        
        input = sys.stdin.readline().rstrip()
        print(input)
        
        if input == '1':
            load_shader_manual_clock(tt, shader_test1)
        elif input == '2':
            load_shader_manual_clock(tt, shader_test2)
        elif input == '3':
            load_shader_manual_clock(tt, shader_test3)
        elif input == '4':
            load_shader_manual_clock(tt, shader_test4)
        elif input == '5':
            load_shader_manual_clock(tt, shader_test5)
        elif input == '6':
            load_shader_manual_clock(tt, shader_test6)
        elif input == '7':
            load_shader_manual_clock(tt, shader_test7)
        elif input == '8':
            load_shader_manual_clock(tt, shader_test8)
        elif input == '9':
            load_shader_manual_clock(tt, shader_test9)
        elif input == 'user':
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
        else:
            load_shader_manual_clock(tt, shader_test1)
    
    #shader_test(tt)
    

"""

busy wait: 80us from falling edge of vsync to start of pulse, pulse is 12us
interrupt: 88us from falling edge of vsync to start of pulse, pulse is 25us

"""


"""
>>> import examples.tt_um_tiny_shader_mole99 as test
>>> test.run()
"""
