import fullcontrol as fc
import math
import numpy as np

def euclidean_distance(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

def find_closest(point, point_list, condition):
    min_distance = float('inf')
    closest_point = None

    for p in point_list:
        if p.z == point.z:
            if (condition == "greater" and p.y > 0) or (condition == "less" and p.y < 0):
                distance = euclidean_distance(point, p)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = p

    return closest_point

def modified_triangle_wave_infill(steps, z, min_x, max_x, infill_density):
    s_density = max_x / infill_density

    # Define a small offset to avoid overlapping with the wall
    offset = 0.085 * max_x

    for i in range(infill_density-1, 0, -1):
        added = max_x - s_density * i
        for condition in ["greater", "less"]:
            coord = fc.Point(x=added, y=0, z=z)
            closest = find_closest(coord, steps, condition)
            if closest is not None:
                steps.append(closest)
    
    # Travel to max_x - offset at the end
    steps.append(fc.Point(x=max_x - offset, y=0, z=z))
    steps.append(fc.Point(x=max_x, y=0, z=z))
    
    return steps
