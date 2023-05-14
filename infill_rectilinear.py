import fullcontrol as fc
import math
import numpy as np

def is_point_in_polygon(point, polygon):
    # Ray casting algorithm to check if a point is inside a polygon
    inside = False
    p1x, p1y = polygon[0]
    for i in range(len(polygon) + 1):
        p2x, p2y = polygon[i % len(polygon)]
        if point.y > min(p1y, p2y):
            if point.y <= max(p1y, p2y):
                if point.x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersect = (point.y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or point.x <= x_intersect:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def rectilinear_infill(steps, z, min_x, max_x, min_y, max_y, infill_density):
    # Calculate the spacing between infill lines based on the desired density
    x_spacing = (max_x - min_x) / infill_density
    y_spacing = (max_y - min_y) / infill_density

    # Create a list of (x, y) tuples representing the airfoil shape
    airfoil = [(point.x, point.y) for point in steps]

    # Create the infill lines in the x-direction
    for i in range(infill_density):
        x = min_x + i * x_spacing
        for j in range(infill_density):
            y = min_y + j * y_spacing
            point = fc.Point(x=x, y=y, z=z)
            if is_point_in_polygon(point, airfoil):
                steps.append(point)

    return steps