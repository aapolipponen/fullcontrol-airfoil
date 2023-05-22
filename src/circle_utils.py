import fullcontrol as fc
import math
import numpy as np

def create_circle_segment(center, radius, num_points, start_theta, end_theta, z):
    segment_points = np.linspace(start_theta, end_theta, num_points)
    points = []
    
    for theta in segment_points:
        x = center.x + radius * np.cos(theta)
        y = center.y + radius * np.sin(theta)
        points.append(fc.Point(x=x, y=y, z=z))
    
    return points

def create_circles(circles, radius, offset, num_points, start_angle_deg, segment_angle_deg, current_z):
    points = []

    # Convert segment angle and start angle to radians
    segment_angle_rad = math.radians(segment_angle_deg)
    start_angle_rad = math.radians(start_angle_deg)

    for circle in circles:
        start_center = circle["start_center"]
        end_center = circle["end_center"]

        # Check if current_z is within the range of this circle
        if start_center.z <= current_z <= end_center.z:
            outer_radius = radius
            inner_radius = radius - offset

            # Create segments for each circle
            num_segments = int(2*math.pi / segment_angle_rad)
            for i in range(num_segments):
                segment_start_angle = start_angle_rad + i * segment_angle_rad
                segment_end_angle = segment_start_angle + segment_angle_rad

                # Use current_z as the z-value for these points
                outer_segment = create_circle_segment(start_center, outer_radius, num_points, segment_start_angle, segment_end_angle, current_z)
                inner_segment = create_circle_segment(start_center, inner_radius, num_points, segment_start_angle, segment_end_angle, current_z)

                # Add segments to points
                points.extend(inner_segment)

                # Move back to the start of the next outer segment
                if i < num_segments - 1:  # except for the last outer segment
                    next_start_angle = start_angle_rad + (i+1) * segment_angle_rad
                    x = start_center.x + inner_radius * np.cos(next_start_angle)
                    y = start_center.y + inner_radius * np.sin(next_start_angle)
                    points.append(fc.Point(x=x, y=y, z=current_z))

                points.extend(outer_segment)

    return points