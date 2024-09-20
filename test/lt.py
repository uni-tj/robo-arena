# Import the module
import line_module

# Use the Line class from the module
from line_module import Line

# Create an instance of Line
origin = (0.0, 0.0)
direction = (1.0, 1.0)
line = Line(origin, direction)

# Use the methods
point = line.g(1.0)
print(f"Point on line at t=1: {point}")

distance = line.distance((1.0, 0.0))
print(f"Distance from point (1, 0) to line: {distance}")
