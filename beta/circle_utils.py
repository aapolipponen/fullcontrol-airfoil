import fullcontrol as fc
import math
import numpy as np

def lerp_points(p1, p2, t):
    return fc.Point(x=(1 - t) * p1.x + t * p2.x, y=(1 - t) * p1.y + t * p2.y, z=(1 - t) * p1.z + t * p2.z)

def draw_circle(center, radius, num_points):
    points = []

    # Calculate points along the circle
    angles = np.linspace(0, 2*np.pi, num_points)
    x_values = center.x + radius * np.cos(angles)
    y_values = center.y + radius * np.sin(angles)

    for x, y in zip(x_values, y_values):
        points.append(fc.Point(x=x, y=y, z=center.z))

    return points

def draw_circles(radiuses, centers, num_points):
    all_points = []

    for radius, center in zip(radiuses, centers):
        # Draw a circle
        circle_points = draw_circle(center, radius, num_points)
        all_points.extend(circle_points)

    return all_points