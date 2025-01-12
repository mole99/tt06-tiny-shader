# Psychedelic dream

# XOR the sine values of X and Y
# and add the current time

GETX R0
SINE R1

GETY R0
SINE R0

XOR R0 R1

GETTIME R1
ADD R0 R1

SETRGB R0
