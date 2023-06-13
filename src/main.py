import time
start = time.time()
import numpy as np
import fullcontrol as fc
from infill_modified_triangle import modified_triangle_wave_infill
from circle_utils import create_circles
from full_fill import fill_shape

def calibration(bed_x_max, bed_y_max):
    calibration = []
    calibration.append(fc.Extruder(on=False))
    calibration.append(fc.Point(x=bed_x_max, y=bed_y_max, z=10))
    calibration.append(fc.Point(x=0, y=0, z=10))
    calibration.append(fc.Extruder(on=True))
    return calibration

def naca_airfoil(naca_num, num_points, chord_length):
    naca_length = len(naca_num)
    if naca_length != 4:
        raise ValueError("Invalid NACA number. Must be 4 digits long.")
    m = int(naca_num[0]) / 100
    p = int(naca_num[1]) / 10 if naca_num[1] != '0' else 0
    t = int(naca_num[2:]) / 100
    x = np.linspace(0, 1, num_points)
    y_t = 5 * t * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    yc = np.where(x < p, m / p**2 * (2 * p * x - x**2) if p != 0 else 0, m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2) if p != 1 else 0)
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

def airfoil_extract(chord_length, filename, interpolate=True, remove_y0=True, sort_point_order=True, reverse_points_sorting=True):
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

def optimize_airfoil(airfoil, multiplier=5):
    fill = []
    for i in range(len(airfoil) - 1):
        point1 = airfoil[i]
        point2 = airfoil[i + 1]

        avg_values = [(val1 + val2) / 2 for val1, val2 in zip((point1.x, point1.y, point1.z), (point2.x, point2.y, point2.z))]
        new_point = fc.Point(x=avg_values[0], y=avg_values[1], z=avg_values[2])

        fill.append(point1)
        fill.extend([new_point]*multiplier)

    fill.append(airfoil[-1])
    return fill

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

def airfoil_wrapper(naca_nums, num_points, z_positions, chord_lengths, naca_airfoil_generation, filenames):
    
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
        for z_value, chord_length, filename in zip(z_positions, chord_lengths, filenames):
            airfoil = airfoil_extract(chord_length, filename)
            airfoil = process_airfoil(airfoil, z_value)
            airfoils.append(airfoil)
    else:
        for naca_num, z_value, chord_length in zip(naca_nums, z_positions, chord_lengths):
            airfoil = naca_airfoil(naca_num, num_points, chord_length)
            airfoil = process_airfoil(airfoil, z_value)
            airfoils.append(airfoil)

    return airfoils

def lerp_points(p1, p2, t):
    x = p1.x * (1 - t) + p2.x * t
    y = p1.y * (1 - t) + p2.y * t
    z = p1.z * (1 - t) + p2.z * t
    return fc.Point(x=x, y=y, z=z)

def loft_shapes():    
    assert len(naca_nums) == len(z_positions) == len(chord_lengths) == len(filenames), "Input lists must have the same length. There is a bug in the code or you have inputted different length lists."

    
    steps = []
    total_layers = sum(int((z_positions[i+1] - z_positions[i]) / layer_height) for i in range(len(z_positions) - 1))
    if print_total_layers:
        print(f"Total layers: {total_layers}")

    for i in range(len(z_positions) - 1):
        num_layers = int((z_positions[i+1] - z_positions[i]) / layer_height)
        current_z = z_positions[i]
        
        chord_length_diff = chord_lengths[i+1] - chord_lengths[i]

        for j in range(num_layers):
            z = current_z + j * layer_height
            
            # Normalized height within current segment
            t = j / num_layers
                       
            # Interpolate chord length
            if curved_wing:
                chord_length = chord_lengths[i] + chord_length_diff * np.sqrt(1 + t**2)           
            else:
                # Linear interpolation
                chord_length = chord_lengths[i] + chord_length_diff * t 

            airfoil = airfoil_wrapper([naca_nums[i]], num_points, [z], [chord_length], file_extraction, [filenames[i]])[0]

            # Move airfoil based on chord lengths if edge is not set as straight
            # Calculating these in a different way leads to a weird bug where the infill spills out.
            # For now this method works.
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

            if generate_infill and not z in filled_layers:
                max_x = max(point.x for point in airfoil)
                if infill_type == modified_triangle_wave_infill:
                    layer.extend(modified_triangle_wave_infill(layer, z, min_x, max_x, infill_density, infill_reverse, layer_height, infill_rise))            
            
            if generate_circle:
                layer.extend(create_circles(circle_centers, circle_radius, circle_offset, circle_num_points, circle_start_angle, circle_segment_angle, z))

            # Check if this z-value should be a fully filled layer
            if z in filled_layers:
                layer.extend(fill_shape(airfoil, line_width, fill_angle, z))

            # After completing the layer, move to next layer.
            steps.extend(fc.travel_to(fc.Point(x=min_x, y=0, z=z+layer_height)))
            
            steps.extend(layer)
    
    return steps

# SETTINGS
# Global Variables

# Airfoil Parameters
naca_nums = ['2412', '2412'] # NACA airfoil numbers (for NACA airfoil method)
num_points = 128 # Resolution of airfoil - higher values give better quality but slower performance and larger file size for gcode

# Wing Parameters
z_positions = [0, 100]  # Z-coordinates for each airfoil section
chord_lengths = [100, 75]  # Chord length for each airfoil section

# File Extraction Parameters (Beta)
file_extraction = False # Enable to use file extraction, disable for NACA airfoil method
filenames = ['mh60.dat', 'mh60.dat'] # File names for file extraction method. These have to be in the profiles folder.

# Infill Parameters
generate_infill = True
infill_density = 6 # Density of infill (higher values = denser infill)
infill_reverse = False # Enable to reverse infill direction
infill_rise = True # Enable to raise infill by half layer height when returning to start point of infill. Makes the hop from layer to layer smaller.
infill_type = modified_triangle_wave_infill # Infill pattern type

# Fully filled airfoil
fill_angle = 45
filled_layers = [0, 0.3, 0.6]

# Circle Generation Parameters
generate_circle = False
circle_centers = [ # Center points for start and end of circle
    {"start_center": fc.Point(x=37.763, y=1.25, z=min(z_positions)), "end_center": fc.Point(x=32.945, y=1.25, z=40)},
]
circle_radius = 4 # Radius of circle
circle_num_points = 24 # Number of points in circle
circle_offset = 0.75 # Offset for second circle
circle_segment_angle = 45 # Angle covered by each pass when drawing circle
circle_start_angle = 180 # Starting angle for circle. Started on the outer circle.

# Wing Curvature Parameters
move_leading_edge = True # Allows movement for the leading edge. If true the edge moves if an chord_length upper in z is smaller.
move_trailing_edge = True # Allows movement for the trailing edge. If true the edge moves if an chord_length upper in z is smaller.

curved_wing = True
curve_type = 'Elliptical' # Options are 'quadratic' and 'elliptical'
curve_amount = 1 # Ellipse curvature amount (1 = fully curved, 0 = not curved)

# Offset
offset_wing = False
offset_x = 50 # Offset in mm (x-axis)
offset_y = 100 # Offset in mm (y-axis)
offset_z = 0 # Offset in mm (z-axis). Adjust if nozzle is digging into the bed during first layer print. The 3D printer's own z offset might not work when using fullcontrol.

# Pre-Print Settings
calibration_moves = False # Enable/disable extra travel move at the start. (Makes the maximum dimensions of the printer be shown in the plot)
bed_x_max = 300
bed_y_max = 300

# Post-Print Settings
z_hop_enabled = False # Makes z move up a set amount after print is done
z_hop_amount = 50 # Height to move extruder up after printing
continuous_wing = True # If enabled ignores the z_positions and chord_lengths between the first and the last values. Kind of a hacky toggle, but it can save time if you don't want to remove values from the lists.

curved_wing = True
ellipse_curvature = 1

# 3D Printing Configuration
# If you want to 3D print instead of just plotting
gcode_generation = False
gcode_name = 'gcode_output' # Output filename for G-code

layer_height = 0.3
line_width = 0.4

# Printer Specific Settings
printer_settings = {
    "extrusion_width": line_width, # Width of extrusion in mm
    "extrusion_height": layer_height, # Height of extrusion in mm
    "print_speed": 2000, # Print speed (acceleration)
    "travel_speed": 4000, # Travel speed (acceleration)
    "nozzle_temp": 210, # Nozzle temperature in degrees Celsius
    "bed_temp": 60, # Bed temperature in degrees Celsius
}

# Debug Setting
print_total_layers = True
print_time_taken = True

# SETTINGS END

steps = loft_shapes()

if offset_wing:
    steps = fc.move(steps, fc.Vector(x=offset_x, y=offset_y, z=offset_z))

if calibration_moves:
    calibration = calibration(bed_x_max, bed_y_max)
    steps = calibration+steps

if z_hop_enabled:
    steps.append(fc.Extruder(on=False))
    steps.append(fc.Point(z=+z_hop_amount))

print("Rendering plot")
fc.transform(steps, 'plot', fc.PlotControls(line_width = line_width*10, color_type='print_sequence', style='tube'))

if gcode_generation:
    print("Generating gcode")
    fc.transform(steps, 'gcode', fc.GcodeControls(save_as=gcode_name, initialization_data=printer_settings))

if print_time_taken:
    end = time.time()
    time_to_generate = end-start
    print('Generated wing in: '+str(round(time_to_generate, 4))+' s')