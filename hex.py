import fullcontrol as fc
import math

# size of the grid
width = 10
height = 10

# radius of each hexagon - this could be any number
r = 1

# list to hold the center points of the hexagons
steps = []

# iterate over the grid
for i in range(height):
    for j in range(width):
        # calculate the center point of the hexagon
        x = j * r * math.sqrt(3) * (1 - 0.5 * (i % 2))
        y = i * r * 1.5
        z = -x-y
        # create the fc.Point and add it to the list
        steps.append(fc.Point(x=x, y=y, z=z))

# now steps contains the center points of the hexagons

# a function to generate the vertices of a hexagon given its center point and radius
def hexagon_vertices(center, r):
    return [fc.Point(center.x + math.cos(math.pi / 3 * i) * r, center.y + math.sin(math.pi / 3 * i) * r, -center.x-center.y) for i in range(6)]

# list to hold the hexagons
hexagons = []

# generate the hexagons
for center in steps:
    hexagons.append(hexagon_vertices(center, r))
    
fc.transform(hexagons, 'plot', fc.PlotControls(color_type='print_sequence'))
