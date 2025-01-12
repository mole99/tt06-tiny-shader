# Use sine values of X and Y to set the colors for R and G
# Add the time for an animation

GETTIME R2

GETX R0
ADD R0 R2
SINE R1
SETR R1

GETY R0
ADD R0 R2
SINE R1
SETG R1
