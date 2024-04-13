# Sine

# Load color white
LDI 63
MOV R3 R0

# Get sine value depending on x
GETX R0

# Set color to x
SETRGB R0

# Get sine value and half it
SINE R0
HALF R0

# Get y
GETY R1

# If sine value is greater than y
# set color to white
IFGE R1
SETRGB R3

NOP
