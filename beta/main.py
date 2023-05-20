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

def airfoil_wrapper(naca_nums, num_points, z_values, chord_lengths, naca_airfoil_generation, filenames):
    
    airfoils = []
    

    def airfoil_extract(chord_length, filename):
        steps = []
        with open(filename, 'r') as file:
            lines = file.readlines()

        # skip the first line as it's a header
        for line in lines[1:]:
            x, y = map(float, line.split())
            steps.append(fc.Point(x=x*chord_length, y=y*chord_length, z=0))
        return steps

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

def create_single_layer(args):
    i, shape1, shape2, z_values, layer_height = args
    num_layers = int((z_values[i+1] - z_values[i]) / layer_height)
    layers = []
    if num_layers > 0:
        for j in range(num_layers):
            t = j / num_layers
            layer = [lerp_points(p1, p2, t) for p1, p2 in zip(shape1, shape2)]
            layers.append(layer)
    return layers

def loft_shapes(airfoils, z_values, layer_height, infill_density, generate_infill, generate_circle, circle_centers, circle_radiuses, circle_num_points, infill_type, infill_reverse, circle_offset, circle_segment_ratio, circle_start_angle):
    layers = []
    circle_layers = []
    steps = []

    for i in range(len(airfoils) - 1):
        shape1, shape2 = airfoils[i], airfoils[i+1]
        layers.append(create_single_layer((i, shape1, shape2, z_values, layer_height)))

    # Flatten the layers list
    layers = [point for sublist in layers for point in sublist]

    for layer in layers:
        steps.extend(layer)

        if generate_infill:
            min_x = min(point.x for point in layer)
            max_x = max(point.x for point in layer)
            if infill_type == modified_triangle_wave_infill:
                steps = modified_triangle_wave_infill(steps, layer[0].z, min_x, max_x, infill_density, infill_reverse)
                
        if generate_circle:
            circle_layers = create_circles(circle_centers, circle_radiuses, circle_offset, layer[0].z, circle_num_points, circle_start_angle, circle_segment_ratio)
        steps.extend(circle_layers)
    
    return steps

# SETTINGS

# 3D printing settings
# NOTE: If you want to enable 3d printing 
# uncomment the things down after fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence'))
layer_height = 0.3
line_width = 0.4

Z_hop = 25 # Move extruder up a set amount (Default = 25) after 3D print is done.

#These are good settings for my 3d printer. Feel free to change them to your settings. 
#The speed values are kinda high so many printers probably wont handle it.
#If printing with infill, make the speed values smaller.
settings = {
    "extrusion_width": line_width,
    "extrusion_height": layer_height,
    "print_speed": 4000,
    "travel_speed": 6000,
    "nozzle_temp": 220,
    "bed_temp": 55,
}

# Airfoil
naca_nums = ['2412', '2412']  # List of NACA airfoil numbers, if generating using naca method
num_points = 128 # The resolution / accuracy of your airfoil (and circle by default).
# resolution graphical quality, generation speed, gcode size (using default settings)
# # 512 = Almost same as 256, really slow, 11,2 MB 
# 256 = Good, somewhat slow, 5.4 MB
# 128 = Default, default, 2.7 MB
# 64 = Worse quality, Fast, 1.3 MB

# File extraction (WARNING: BETA, May not work correctly.)
file_extraction = False # If you want to extract data from a file. False If you want to use the 4-Digit NACA airfoil method for generating airfoils instead.
filenames = ['data.dat', 'data.dat'] # If you want to extract the coordinates from a file.

# Wing parameters
z_values = [0, 40]  # List of z-values for the airfoils
chord_lengths = [100, 75]  # Chord lengths of the airfoils

airfoils = airfoil_wrapper(naca_nums, num_points, z_values, chord_lengths, file_extraction, filenames)

# Infill
generate_infill = True
infill_density = 8 # How dense the infill is.
infill_reverse = False # Use if using file_extraction and starting point for airfoil is closer to or at the max x coordinate.
infill_type = modified_triangle_wave_infill # Default and recommended = modified_triangle_wave_infill. 
# No other infill options at this moment. Create your own one!

# Circle generation
generate_circle = True
circle_centers = [
    [fc.Point(x=28.5, y=1.75, z=min(z_values)), fc.Point(x=28.5, y=1.75, z=max(z_values))], 
]
circle_radiuses = 3.5
circle_num_points = 24

circle_offset = 0.75 # Offset of the second circle being generated
circle_segment_ratio = 45 # How much of the circle is drawn in one pass (angle)
circle_start_angle = 90 # Start angle for the circle.

steps = loft_shapes(airfoils, z_values, layer_height, infill_density, generate_infill, generate_circle, circle_centers, circle_radiuses, circle_num_points, infill_type, infill_reverse, circle_offset, circle_segment_ratio, circle_start_angle)

# Offset the generated airfoil.
# If 3D printing make sure to double check this,
# because it might be different on different printers and airfoils.
offset_x = 50
offset_y = 100
offset_z = 0 # If the nozzle is digging to the bed while printing the first layer and printers own z offset is adjusted correctly.
# The 3D printers own z offset might not work using fullcontrol.
 
#steps = fc.move(steps, fc.Vector(x=offset_x, y=offset_y, z=offset_z))

# Show the bed / build area size, with the cost of an extra travel move at the start of the gcode.
# Works also without 3d printing
calibration = calibration(bed_x_max = 300, bed_y_max = 300)
steps = calibration+steps

## Move extruder up a set amount (Default = 25) after 3D print is done.
steps.append(fc.Extruder(on=False))
steps.append(fc.Point(z=+Z_hop))

fc.transform(steps, 'plot', fc.PlotControls(line_width = line_width*10, color_type='print_sequence'))

# Uncomment if you want to 3D print / generate GCODE.
#fc.transform(steps, 'gcode', fc.GcodeControls(save_as='my_design', initialization_data=settings))