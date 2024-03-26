# Black and white horizontal stripes

GETY R1
LDI 1
AND R1 R0

IFNE R1
LDI 63

IFEQ R1
LDI 0

SETRGB R0
