import fullcontrol as fc
import math
import numpy as np

def create_circle_segment(center, radius, num_points, start_theta, end_theta, start_angle, z):
    segment_points = np.linspace(start_theta, end_theta, num_points)
    points = []
    
    for theta in segment_points:
        x = center.x + radius * np.cos(theta + start_angle)
        y = center.y + radius * np.sin(theta + start_angle)
        points.append(fc.Point(x=x, y=y, z=z))
    
    return points

def create_circles(center_pairs, radius, offset, z, num_points, start_angle_deg, segment_angle_deg):
    points = []

    # Convert segment angle and start angle to radians
    segment_angle_rad = math.radians(segment_angle_deg)
    start_angle_rad = math.radians(start_angle_deg)

    for center_pair in center_pairs:
        start_center, end_center = center_pair

        for center in (start_center, end_center):
            # If z is not within the bounds, use center.z
            if z is not None and start_center.z <= z <= end_center.z:
                center.z = z

            outer_radius = radius
            inner_radius = radius - offset

            # Create segments for each circle
            num_segments = int(2*math.pi / segment_angle_rad)
            for i in range(num_segments):
                segment_start_angle = start_angle_rad + i * segment_angle_rad
                segment_end_angle = segment_start_angle + segment_angle_rad

                outer_segment = create_circle_segment(center, outer_radius, num_points, segment_start_angle, segment_end_angle, start_angle_rad, z)
                inner_segment = create_circle_segment(center, inner_radius, num_points, segment_start_angle, segment_end_angle, start_angle_rad, z)

                # Add segments to points alternately
                points.extend(outer_segment)
                points.extend(inner_segment)

    return points