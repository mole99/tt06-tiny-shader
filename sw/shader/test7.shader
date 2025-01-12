# Draw a rectified sine wave

CLEAR R3

# Get X coord (and add time)
GETX R0
GETTIME R1
ADD R0 R1

# Set color to X
SETRGB R0

# Get sine value for X and halve it
SINE R0
HALF R0

# If sine value is greater than Y
# clear color to black
GETY R1
IFGE R1
SETRGB R3
