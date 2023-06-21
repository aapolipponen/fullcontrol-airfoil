import numpy as np
import fullcontrol as fc

def rotate_point(point, angle, z):
    """ Rotate a point counter-clockwise by a given angle around the origin (0,0).
    """
    angle = np.radians(angle)  # Convert degrees to radians
    px, py = point.x, point.y
    qx = np.cos(angle)*px - np.sin(angle)*py
    qy = np.sin(angle)*px + np.cos(angle)*py
    return fc.Point(x=qx, y=qy, z=z)

def fill_shape(points, line_width, angle, z):
    fill_points = []

    # Rotate points by given angle
    rotated_points = [rotate_point(p, angle, z) if isinstance(p, fc.Point) else p for p in points]

    # Get the min and max y values of the rotated shape
    min_y = min(point.y for point in rotated_points if isinstance(point, fc.Point))
    max_y = max(point.y for point in rotated_points if isinstance(point, fc.Point))

    # For each y value between min_y and max_y with a step size of line_width
    y_values = np.arange(min_y, max_y + line_width, line_width)

    # Initialize the last point to None
    last_point = None

    # For each y value
    for y in y_values:
        intersections = []

        # Check each line segment in the polygon for intersection with this y value
        for i in range(len(rotated_points)):
            p1 = rotated_points[i]
            if not isinstance(p1, fc.Point):
                continue
            p2 = rotated_points[(i+1)%len(rotated_points)]
            if not isinstance(p2, fc.Point):
                continue

            # If this line segment intersects with this y value
            if min(p1.y, p2.y) < y <= max(p1.y, p2.y):
                # Compute the x-coordinate of the intersection point
                x = p1.x + (p2.x - p1.x) * (y - p1.y) / (p2.y - p1.y)
                intersections.append(x)

        # Sort the intersections to pair them up
        intersections.sort()

        # Generate the lines from these intersection points
        for i in range(0, len(intersections) - 1, 2):
            if i+1 < len(intersections):
                line_start = rotate_point(fc.Point(x=intersections[i], y=y, z=z), -angle, z)
                line_end = rotate_point(fc.Point(x=intersections[i+1], y=y, z=z), -angle, z)
                
                # Check if the line should start from the last end point
                if last_point and np.linalg.norm(np.array([line_start.x, line_start.y]) - np.array([last_point.x, last_point.y])) > np.linalg.norm(np.array([line_end.x, line_end.y]) - np.array([last_point.x, last_point.y])):
                    line_start, line_end = line_end, line_start

                # Add the start and end points of the line to the fill_points list
                fill_points.extend(fc.travel_to(line_start))  # use extend instead of append
                fill_points.append(line_end)

                # Update the last point
                last_point = line_end

    # Ensure the first point in fill_points is a fc.Point instance before calling fc.travel_to
    if isinstance(fill_points[0], fc.Point):
        fill_points.extend(fc.travel_to(fill_points[0]))

    return fill_points