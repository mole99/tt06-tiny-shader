# Colored Circles (morphing)

# Sine value of X in R2
GETX R0
SINE R2

# Sine value of Y in R0
GETY R0
SINE R0

# Add the colors up in R0
ADD R0 R2

GETTIME R1

# Add the colors up in R0
ADD R0 R1

GETUSER R1

# Add the colors up in R0
ADD R0 R1

# Output
SETRGB R0
