import time
start = time.time()
import numpy as np
import fullcontrol as fc
from infill_modified_triangle import modified_triangle_wave_infill
from circle_utils import create_circles

def calibration(bed_x_max, bed_y_max):
    calibration = []
    calibration.append(fc.Extruder(on=False))
    calibration.append(fc.Point(x=bed_x_max, y=bed_y_max, z=10))
    calibration.append(fc.Point(x=0, y=0, z=10))
    calibration.append(fc.Extruder(on=True))
    return calibration

def naca_airfoil(naca_num, num_points, chord_length):
    naca_length = len(naca_num)
    if naca_length != 4 and naca_length != 3:
        raise ValueError("Invalid NACA number. Must be 4 digits long.")
    m = int(naca_num[0]) / 100
    p = int(naca_num[1]) / 10
    t = int(naca_num[2:]) / 100
    x = np.linspace(0, 1, num_points)
    y_t = 5 * t * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    yc = np.where(x < p, m / p**2 * (2 * p * x - x**2), m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2))
    theta = np.arctan(np.gradient(yc, x))
    xu = x - y_t * np.sin(theta)
    xl = x + y_t * np.sin(theta)
    yu = yc + y_t * np.cos(theta)
    yl = yc - y_t * np.cos(theta)
    xu *= chord_length
    yu *= chord_length
    xl *= chord_length
    yl *= chord_length
    steps_upper = [fc.Point(x=xu[i], y=yu[i], z=0) for i in range(num_points)]
    steps_lower = [fc.Point(x=xl[i], y=yl[i], z=0) for i in range(num_points - 1, -1, -1)]
    steps = steps_upper + steps_lower
    return steps

def airfoil_extract(chord_length, filename, interpolate=True, remove_y0=True, sort_point_order=True, reverse_points_sorting=False):
    airfoil = []
    with open("profiles/" + filename, 'r') as file:
        lines = file.readlines()
    for line in lines[1:]:
        x, y = map(float, line.split())
        airfoil.append(fc.Point(x=x * chord_length, y=y * chord_length, z=0))
    if interpolate:
        airfoil = optimize_airfoil(airfoil)
    if remove_y0:
        airfoil = (point for point in airfoil if point.y != 0)
    if sort_point_order:
        airfoil = sort_points(airfoil, reverse_points_sorting)
    return airfoil

def optimize_airfoil(airfoil, multiplier=2):
    new_points = []
    for i in range(len(airfoil) - 1):
        point1 = airfoil[i]
        point2 = airfoil[i + 1]

        avg_values = [(val1 + val2) / 2 for val1, val2 in zip((point1.x, point1.y, point1.z), (point2.x, point2.y, point2.z))]
        new_point = fc.Point(x=avg_values[0], y=avg_values[1], z=avg_values[2])

        new_points.append(point1)
        new_points.extend([new_point]*multiplier)

    new_points.append(airfoil[-1])
    return new_points

def remove_points_y0(airfoil):
    airfoil = [point for point in airfoil if point.y != 0]
    return airfoil

def sort_points(points, reverse_order):
    points_over_y0 = []
    points_under_y0 = []

    for point in points:
        (points_over_y0 if point.y > 0 else points_under_y0).append(point)

    points_over_y0.sort(key=lambda point: point.x, reverse=reverse_order)
    points_under_y0.sort(key=lambda point: point.x, reverse=not reverse_order)

    return points_over_y0 + points_under_y0

def airfoil_wrapper(naca_nums, num_points, z_values, chord_lengths, naca_airfoil_generation, filenames):
    
    airfoils = []
    
    def airfoil_extract(chord_length, filename, interpolate=True, remove_y0=True, sort_point_order=True, reverse_points_sorting=False):
        airfoil = []
        with open("profiles/"+filename, 'r') as file:
            lines = file.readlines()
        # Skip the first line as it's a header
        for line in lines[1:]:
            x, y = map(float, line.split())
            airfoil.append(fc.Point(x=x*chord_length, y=y*chord_length, z=0))
        if interpolate:
            airfoil = optimize_airfoil(airfoil)
        if remove_y0:
            airfoil = remove_points_y0(airfoil)
        if sort_point_order:
            airfoil = sort_points(airfoil, reverse_points_sorting)
        steps = airfoil
        return steps
    
    def process_airfoil(airfoil, z_value):
        return [fc.Point(x=point.x, y=point.y, z=z_value) for point in airfoil]
    
    if naca_airfoil_generation:
        for z_value, chord_length, filename in zip(z_values, chord_lengths, filenames):
            airfoil = airfoil_extract(chord_length, filename)
            airfoil = process_airfoil(airfoil, z_value)
            airfoils.append(airfoil)
    else:
        for naca_num, z_value, chord_length in zip(naca_nums, z_values, chord_lengths):
            airfoil = naca_airfoil(naca_num, num_points, chord_length)
            airfoil = process_airfoil(airfoil, z_value)
            airfoils.append(airfoil)

    return airfoils

def lerp_points(p1, p2, t):
    x = p1.x * (1 - t) + p2.x * t
    y = p1.y * (1 - t) + p2.y * t
    z = p1.z * (1 - t) + p2.z * t
    return fc.Point(x=x, y=y, z=z)

def loft_shapes(naca_nums, num_points, file_extraction, filenames, z_values, chord_lengths, layer_height, infill_density, generate_infill, generate_circle, circle_centers, circle_radius, circle_num_points, infill_type, infill_reverse, infill_rise, circle_offset, circle_segment_angle, circle_start_angle, elliptical_wing, move_leading_edge, move_trailing_edge, ellipse_amount):
    steps = []

    for i in range(len(z_values) - 1):
        num_layers = int((z_values[i+1] - z_values[i]) / layer_height)
        current_z = z_values[i]  # Store the current z value
        
        chord_length_diff = chord_lengths[i+1] - chord_lengths[i]

        for j in range(num_layers):
            z = current_z + j * layer_height

            # Normalized height within current segment
            t = j / num_layers
            
            # Interpolate chord length
            if elliptical_wing:
                # Quadratic interpolation
                chord_length = chord_lengths[i] + chord_length_diff * (t**2) * ellipse_amount
            else:
                # Linear interpolation
                chord_length = chord_lengths[i] + chord_length_diff * t 

            airfoil = airfoil_wrapper([naca_nums[i]], num_points, [z], [chord_length], file_extraction, [filenames[i]])[0]

            # Move airfoil based on chord lengths if edge is not set as static
            if move_trailing_edge:
                if move_leading_edge:
                    delta_x = (chord_lengths[i] - chord_length) / 2
                    for point in airfoil:
                        point.x += delta_x
                else:
                    pass
                
            elif move_leading_edge:
                delta_x = (chord_lengths[i] - chord_length)
                for point in airfoil:
                    point.x += delta_x

            else:
                delta_x = (chord_lengths[i] - chord_length) / 2
                for point in airfoil:
                    point.x += delta_x
                    
            layer = airfoil

            min_x = min(point.x for point in airfoil)

            if generate_infill:
                max_x = max(point.x for point in airfoil)
                if infill_type == modified_triangle_wave_infill:
                    layer.extend(modified_triangle_wave_infill(layer, z, min_x, max_x, infill_density, infill_reverse, layer_height, infill_rise))
            
            if generate_circle:
                layer.extend(create_circles(circle_centers, circle_radius, circle_offset, circle_num_points, circle_start_angle, circle_segment_angle, z))
        
            # After completing the layer, move to next layer.
            steps.extend(fc.travel_to(fc.Point(x=min_x, y=0, z=z+layer_height)))
            
            steps.extend(layer)
    
    return steps

def rotate_point(point, angle):
    """ Rotate a point counter-clockwise by a given angle around the origin (0,0).
    """
    angle = np.radians(angle)  # convert degrees to radians
    px, py = point.x, point.y
    qx = np.cos(angle)*px - np.sin(angle)*py
    qy = np.sin(angle)*px + np.cos(angle)*py
    return fc.Point(x=qx, y=qy, z=0)

def fill_shape_with_lines(points, angle=45):
    # Store new points
    new_points = []

    # Rotate points by given angle
    rotated_points = [rotate_point(p, angle) if isinstance(p, fc.Point) else p for p in points]
    
    # Get the min and max y values of the rotated shape
    min_y = min(point.y for point in rotated_points if isinstance(point, fc.Point))
    max_y = max(point.y for point in rotated_points if isinstance(point, fc.Point))

    # Define the step size for the y values. Here we use 1.0, but it could be any positive number
    step_size = 1.0

    # For each y value between min_y and max_y with a step size of step_size
    for y in np.arange(min_y, max_y + step_size, step_size):
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
                line_start = rotate_point(fc.Point(x=intersections[i], y=y, z=0), -angle)
                line_end = rotate_point(fc.Point(x=intersections[i+1], y=y, z=0), -angle)

                # Add the start and end points of the line to the new_points list
                if isinstance(line_start, fc.Point):
                    new_points.extend(fc.travel_to(line_start))  # use extend instead of append
                else:
                    new_points.append(line_start)

                if isinstance(line_end, fc.Point):
                    new_points.append(line_end)
                else:
                    new_points.append(line_end)

    # Ensure the first point in new_points is a fc.Point instance before calling fc.travel_to
    if isinstance(new_points[0], fc.Point):
        new_points.extend(fc.travel_to(new_points[0]))

    return new_points  # return the new

# SETTINGS

# Airfoil Parameters
naca_nums = ['2412', '2412'] # NACA airfoil numbers (for NACA airfoil method)
num_points = 128 # Resolution of airfoil - higher values give better quality but slower performance and larger file size for gcode

# Wing Parameters
z_positions = [0, 0.3]  # Z-coordinates for each airfoil section
chord_lengths = [100, 100]  # Chord length for each airfoil section

# File Extraction Parameters (Beta)
file_extraction = False # Enable to use file extraction, disable for NACA airfoil method
filenames = ['naca2412.dat', 'naca2412.dat'] # File names for file extraction method. These have to be in the profiles folder.

# Infill Parameters
generate_infill = False

infill_density = 8 # Density of infill (higher values = denser infill)
infill_reverse = False # Enable to reverse infill direction
infill_rise = False # Enable to raise infill by half layer height when returning to start point of infill
infill_type = modified_triangle_wave_infill # Infill pattern type

# Circle Generation Parameters
generate_circle = False

circle_centers = [ # Center points for start and end of circle
    {"start_center": fc.Point(x=37.763, y=1.25, z=min(z_positions)), "end_center": fc.Point(x=32.945, y=1.25, z=40)},
]

circle_radius = 4 # Radius of circle
circle_num_points = 24 # Number of points in circle
circle_offset = 0.75 # Offset for second circle
circle_segment_angle = 45 # Angle covered by each pass when drawing circle
circle_start_angle = 180 # Starting angle for circle

# Wing Curvature Parameters
angled_leading_edge = False # Allows movement for the leading edge
angled_trailing_edge = True # Allows movement for the trailing edge

elliptical_wing = False
ellipse_amount = 0.5 # Ellipse curvature amount

# 3D Printing Configuration
gcode_generation = False
gcode_name = 'gcode_output' # Output filename for G-code

# Layer Settings
layer_height = 0.3
line_width = 0.4

# Post-Print Settings
Z_hop = 25 # Height to move extruder up after printing

# Printer Specific Settings
#NOTE: Adjust these values depending on your specific printer and generated airfoil!

# Calibration move
calibration_moves = False # Enable/disable extra travel move at the start. (Makes the maximum dimensions of the printer be shown in the plot)
bed_x_max = 300
bed_y_max = 300

# Offset for wing
offset_x = 50 # Offset in mm (x-axis)
offset_y = 100 # Offset in mm (y-axis)
offset_z = 0 # Offset in mm (z-axis). Adjust if nozzle is digging into the bed during first layer print.
# The 3D printer's own z offset might not work using fullcontrol.

printer_settings = {
    "extrusion_width": line_width, # Width of extrusion in mm
    "extrusion_height": layer_height, # Height of extrusion in mm
    "print_speed": 2000, # Print speed (acceleration)
    "travel_speed": 4000, # Travel speed (acceleration)
    "nozzle_temp": 210, # Nozzle temperature in degrees Celsius
    "bed_temp": 60, # Bed temperature in degrees Celsius
}

steps = loft_shapes(naca_nums, num_points, file_extraction, filenames, z_positions, chord_lengths, layer_height, infill_density, generate_infill, generate_circle, circle_centers, circle_radius, circle_num_points, infill_type, infill_reverse, infill_rise, circle_offset, circle_segment_angle, circle_start_angle, elliptical_wing, angled_leading_edge, angled_trailing_edge, ellipse_amount)

steps = fill_shape_with_lines(steps)

#steps = fc.move(steps, fc.Vector(x=offset_x, y=offset_y, z=offset_z))
#
#calibration = calibration(bed_x_max, bed_y_max)
#steps = calibration+steps
#
#steps.append(fc.Extruder(on=False))
#steps.append(fc.Point(z=+Z_hop))

fc.transform(steps, 'plot', fc.PlotControls(line_width = line_width*10, color_type='print_sequence'))

#if gcode_generation:
#    fc.transform(steps, 'gcode', fc.GcodeControls(save_as=gcode_name, initialization_data=printer_settings))
#
#end = time.time()
#time_to_generate = end-start
#print('Generated in: '+str(round(time_to_generate, 5))+' s')