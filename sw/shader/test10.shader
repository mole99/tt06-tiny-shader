# Colored Circles (moving)

# Sine value of X+Time in R2
GETX R0
GETTIME R1
ADD R0 R1
SINE R2

# Sine value of Y+Time in R0
GETY R0
GETTIME R1
ADD R0 R1
SINE R0

# Add the colors up
ADD R0 R2

# Output
SETRGB R0
