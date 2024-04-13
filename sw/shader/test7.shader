# Sine

# Clear R3
CLEAR R3

# Get sine value depending on x
GETX R0
GETUSER R1
ADD R0 R1

# Set color to x
SETRGB R0

# Get sine value and half it
SINE R0
HALF R0

# Get y
GETY R1

# If sine value is greater than y
# set color to black
IFGE R1
SETRGB R3
