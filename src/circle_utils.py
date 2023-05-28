import fullcontrol as fc
import math
import numpy as np

def create_circle_segment(center, radius, num_points, start_theta, end_theta, z):
    segment_points = np.linspace(start_theta, end_theta, num_points)
    x = center.x + radius * np.cos(segment_points)
    y = center.y + radius * np.sin(segment_points)
    points = [fc.Point(x=x[i], y=y[i], z=z) for i in range(num_points)]
    return points

def lerp(a, b, t):
    return a * (1 - t) + b * t

def create_circles(circles, radius, offset, num_points, start_angle_deg, segment_angle_deg, current_z):
    steps = []

    # Convert segment angle and start angle to radians
    segment_angle_rad = math.radians(segment_angle_deg)
    start_angle_rad = math.radians(start_angle_deg)

    for circle in circles:
        start_center = circle["start_center"]
        end_center = circle["end_center"]

        # Calculate interpolation factor based on current_z
        z_range = end_center.z - start_center.z
        if z_range != 0:
            t = (current_z - start_center.z) / z_range
        else:
            t = 0

        # Interpolate center position
        center_x = lerp(start_center.x, end_center.x, t)
        center_y = lerp(start_center.y, end_center.y, t)
        center_z = lerp(start_center.z, end_center.z, t)
        center = fc.Point(x=center_x, y=center_y, z=center_z)

        outer_radius = radius
        inner_radius = radius - offset

        # Create segments for each circle
        num_segments = int(2*math.pi / segment_angle_rad)
        
        # Travel to the start of the first segment
        start_angle = start_angle_rad
        x_start = center.x + outer_radius * np.cos(start_angle)
        y_start = center.y + outer_radius * np.sin(start_angle)
        steps.extend(fc.travel_to(fc.Point(x=x_start, y=y_start, z=center.z)))

        for i in range(num_segments):
            segment_start_angle = start_angle_rad + i * segment_angle_rad
            segment_end_angle = segment_start_angle + segment_angle_rad

            outer_segment = create_circle_segment(center, outer_radius, num_points, segment_start_angle, segment_end_angle, center_z)
            inner_segment = create_circle_segment(center, inner_radius, num_points, segment_start_angle, segment_end_angle, center_z)

            # Add segments to steps
            steps.extend(outer_segment)
            steps.extend(inner_segment)

    return steps