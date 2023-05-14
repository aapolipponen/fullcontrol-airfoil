import fullcontrol as fc
import math

def custom_distance_2d(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def find_closest(point, point_list, condition):
    filtered_points = [p for p in point_list if (p.z == point.z) and 
                       ((condition == "greater" and p.y > 0) or (condition == "less" and p.y < 0))]

    return min(filtered_points, key=lambda p: custom_distance_2d(point, p), default=None)

def triangle_wave_infill(steps, z, max_x, infill_density):
    s_density = max_x / infill_density

    # Define a small offset to avoid overlapping with the wall
    offset = 0.1 * max_x

    # Start from the point slightly inside the maximum x-coordinate
    steps.append(fc.Point(x=max_x - offset, y=0, z=z))

    for i in range(1, infill_density):
        added = (s_density * i) - offset
        condition = "less" if i % 2 == 0 else "greater"
        coord = fc.Point(x=added, y=0, z=z)
        closest = find_closest(coord, steps, condition)
        if closest is not None:
            steps.append(closest)

    # Travel to max_x - offset at the end
    steps.append(fc.Point(x=max_x - offset, y=0, z=z))
    steps.append(fc.Point(x=max_x, y=0, z=z))

    return steps