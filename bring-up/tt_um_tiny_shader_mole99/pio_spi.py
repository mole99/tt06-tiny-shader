# SPI using PIO, which is handy because you can use any pins.

import rp2
from machine import Pin

@rp2.asm_pio(out_shiftdir=0, autopull=True, pull_thresh=8, autopush=True, push_thresh=8, sideset_init=(rp2.PIO.OUT_LOW,), out_init=rp2.PIO.OUT_LOW)
def spi_cpha0():
    out(pins, 1)             .side(0x0)
    in_(pins, 1)             .side(0x1)

@rp2.asm_pio(out_shiftdir=0, autopull=True, pull_thresh=8, autopush=True, push_thresh=8, sideset_init=(rp2.PIO.OUT_LOW,), out_init=rp2.PIO.OUT_LOW)
def spi_cpha1():
    pull(ifempty)            .side(0x0)
    out(pins, 1)             .side(0x1).delay(1)
    in_(pins, 1)             .side(0x0)
    
class PIOSPI:

    def __init__(self, sm_id, pin_mosi, pin_miso, pin_sck, cpha=False, cpol=False, freq=1000000):
        assert(not(cpol))
        if not cpha:
            self._sm = rp2.StateMachine(sm_id, spi_cpha0, freq=2*freq, sideset_base=Pin(pin_sck), out_base=Pin(pin_mosi), in_base=Pin(pin_miso))
        else:
            self._sm = rp2.StateMachine(sm_id, spi_cpha1, freq=4*freq, sideset_base=Pin(pin_sck), out_base=Pin(pin_mosi), in_base=Pin(pin_miso))
        self._sm.active(1)

    @micropython.native
    def write(self, wdata):
        first = True
        for b in wdata:
            self._sm.put(b, 24)
            if not first:
                self._sm.get()
            else:
                first = False
        self._sm.get()
        
    def read(self, n):
        return self.write_read_blocking([0,]*n)

    @micropython.native
    def readinto(self, rdata):
        self._sm.put(0)
        for i in range(len(rdata)-1):
            self._sm.put(0)
            rdata[i] = self._sm.get()
        rdata[-1] = self._sm.get()

    @micropython.native
    def write_read_blocking(self, wdata):
        rdata = bytearray(len(wdata))
        i = -1
        for b in wdata:
            self._sm.put(b, 24)
            if i >= 0:
                rdata[i] = self._sm.get()
            i += 1
        rdata[i] = self._sm.get()
        return rdata
