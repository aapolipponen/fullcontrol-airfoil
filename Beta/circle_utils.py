import fullcontrol as fc
import math
import numpy as np

def create_circle(center, radius, num_points):
    points = []
    for i in range(num_points):
        angle = 2 * np.pi * i / num_points
        x = center.x + radius * np.cos(angle)
        y = center.y + radius * np.sin(angle)
        z = center.z
        point = fc.Point(x=x, y=y, z=z)
        points.append(point)
        if i == 0:
            first_point = (x, y)
    return points, first_point

def lerp_points(p1, p2, t):
    x = p1.x * (1 - t) + p2.x * t
    y = p1.y * (1 - t) + p2.y * t
    z = p1.z * (1 - t) + p2.z * t
    return fc.Point(x=x, y=y, z=z)

def generate_circle_layers(circle_centers, circle_radiuses, circle_num_points, layer_height):
    layers = []

    for i, (center1, center2) in enumerate(zip(circle_centers[:-1], circle_centers[1:])):
        num_layers = int((center2.z - center1.z) / layer_height)
        if num_layers > 0:
            for j in range(num_layers):
                t = j / num_layers
                current_center = lerp_points(center1, center2, t)
                current_radius = circle_radiuses[i] * (1 - t) + circle_radiuses[i + 1] * t
                layer, first_point = create_circle(current_center, current_radius, circle_num_points)
                layers.append(layer)
                if j == 0:
                    fc.travel_to(fc.Point(x=first_point[0], y=first_point[1], z=current_center.z))

    return layers

def is_point_inside_circle(point, center, radius):
    distance = math.sqrt((point.x - center.x) ** 2 + (point.y - center.y) ** 2)
    return distance <= radius

def remove_intersecting_points(points, center, radius):
    non_intersecting_points = []
    for point in points:
        if not is_point_inside_circle(point, center, radius):
            non_intersecting_points.append(point)
    return non_intersecting_points