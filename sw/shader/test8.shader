# Draw a rectified sine wave

CLEAR R3

# Get Y coord (and add time)
GETY R0
GETTIME R1
ADD R0 R1

# Set color to Y
SETRGB R0

# Get sine value for Y and halve it
SINE R0
HALF R0

# If sine value is greater than X
# clear color to black
GETX R1
IFGE R1
SETRGB R3
