# Hello World!
# Draw one vertical and one horizontal line
# at X=10, Y=10

CLEAR R0
SETRGB R0

GETX R1
GETY R2

LDI 10

IFEQ R1
SETRGB R1

IFEQ R2
SETRGB R2
