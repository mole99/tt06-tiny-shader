# This is a special shader that
# only works on real hardware

# Each pixel (line) shifts R0 one to the left,
# if R0 is zero it is set to TIME
# R0 is then written into RGB

DOUBLE R0
SETRGB R0

CLEAR R3
IFEQ R3
GETTIME R0
