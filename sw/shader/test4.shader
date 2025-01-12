# Xor both coordinates and write to rgb
# Add the time for an animation

GETX R0
GETY R1

XOR R0 R1

GETTIME R2
ADD R0 R2

SETRGB R0
