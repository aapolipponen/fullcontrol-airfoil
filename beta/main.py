import numpy as np
import fullcontrol as fc
import math
from infill_modified_triangle import modified_triangle_wave_infill
from infill_rectilinear import rectilinear_infill
from circle_utils import draw_circles, lerp_points, draw_circle
import concurrent.futures


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
        steps_upper = []
        steps_lower = []
        x = np.linspace(0, 1, num_points)
        if len(naca_num) == 4 or len(naca_num) == 3:
            m = int(naca_num[0]) / 100
            p = int(naca_num[1]) / 10
            t = int(naca_num[2:]) / 100
            y_t = 5*t * (0.2969*np.sqrt(x) - 0.126*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
            if p == 0:
                yc = np.zeros_like(x)
            elif m == 0:
                yc = np.zeros_like(x)
            else:
                yc = np.where(x < p, m/p**2 * (2*p*x - x**2), m/(1-p)**2 * ((1-2*p) + 2*p*x - x**2))
        else:
            raise ValueError("Invalid NACA number. Must be 4 digits long.")

        theta = np.arctan(np.gradient(yc, x))
        xu = x - y_t * np.sin(theta)
        xl = x + y_t * np.sin(theta)
        yu = yc + y_t * np.cos(theta)
        yl = yc - y_t * np.cos(theta)
        xu *= chord_length
        yu *= chord_length
        xl *= chord_length
        yl *= chord_length
        for i in range(num_points):
            steps_upper.append(fc.Point(x=xu[i], y=yu[i], z=0))
        for i in range(num_points-1, -1, -1):
            steps_lower.append(fc.Point(x=xl[i], y=yl[i], z=0))

        steps = steps_upper + steps_lower
        return steps
    
    if naca_airfoil_generation:
        for z_value, chord_length, filename in zip(z_values, chord_lengths, filenames):
            airfoil = airfoil_extract(chord_length, filename)
            airfoil = [fc.Point(x=point.x, y=point.y, z=z_value) for point in airfoil]
            airfoils.append(airfoil)
    else:
        for naca_num, z_value, chord_length in zip(naca_nums, z_values, chord_lengths):
            airfoil = naca_airfoil(naca_num, num_points, chord_length)
            airfoil = [fc.Point(x=point.x, y=point.y, z=z_value) for point in airfoil]
            airfoils.append(airfoil)

    return airfoils

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

def loft_shapes(airfoils, z_values, layer_height, infill_density, generate_infill, generate_circle, circle_centers, circle_radiuses, circle_num_points, infill_type, infill_reverse):
    layers = []
    for i, (shape1, shape2) in enumerate(zip(airfoils[:-1], airfoils[1:])):
        # Generate the airfoil layer
        layer = create_single_layer((i, shape1, shape2, z_values, layer_height))
        # If circles are to be generated, generate them here
        if generate_circle:
            # Assume that each airfoil layer has corresponding circle center and radius
            circle_center = circle_centers[i]
            circle_radius = circle_radiuses[i]
            # Generate the circle for this layer
            circle_points = draw_circle(circle_center, circle_radius, circle_num_points)
            # Extend the layer with circle points
            layer.extend(circle_points)
        # Extend the layers with this layer's points
        layers.extend(layer)

    steps = []

    for point in layers:
        steps.append(point)

    print(dir(layers[0]))

    if generate_infill:
        min_x = min(point.x for point in layers)
        max_x = max(point.x for point in layers)
        min_y = min(point.y for point in layers)
        max_y = max(point.y for point in layers)
        if infill_type == modified_triangle_wave_infill:
            steps = modified_triangle_wave_infill(steps, point.z, min_x, max_x, infill_density, infill_reverse)
        else:
            steps = infill_type(steps, point.z, min_x, max_x, min_y, max_y, infill_density)

    return steps

# SETTINGS

# 3D printing settings
# NOTE: If you want to enable 3d printing 
# uncomment the things down after fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence'))
layer_height = 0.3
line_width = 0.4
## Move extruder up a set amount (Default = 25) after 3D print is done.
Z_hop = 25 

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
z_values = [0, 2]  # List of z-values for the airfoils
chord_lengths = [210, 210]  # Chord lengths of the airfoils

airfoils = airfoil_wrapper(naca_nums, num_points, z_values, chord_lengths, file_extraction, filenames)

# Infill
generate_infill = True
infill_density = 8 # How dense the infill is.
infill_reverse = False # Use if using file_extraction and starting point for airfoil is closer to or at the max x coordinate.
infill_type = modified_triangle_wave_infill # Default and recommended = modified_triangle_wave_infill. 
# Other options are: triangle_wave_infill, sawtooth_wave_infill and rectilinear_infill

# Circle generation
generate_circle = True
circle_radiuses = [5, 5]
circle_centers = [fc.Point(x=70, y=7.5, z=0), fc.Point(x=70, y=7.5, z=max(z_values))]
circle_num_points = 15

circle_offset = 1 # Offset of the second circle being generated
circle_segment_ratio = 20 # How much of the circle is drawn in one pass
circle_start_angle = 270 # Start angle for the outer circle.

steps = loft_shapes(airfoils, z_values, layer_height, infill_density, generate_infill, generate_circle, circle_centers, circle_radiuses, circle_num_points, infill_type, infill_reverse)

# Debug
#print(steps)
#print(airfoils)

# Offset the generated airfoil.
# If 3D printing make sure to double check this,
# because it might be different on different printers and airfoils.
offset_x = 50
offset_y = 100
offset_z = 0 # If the nozzle is digging to the bed while printing the first layer and printers own z offset is adjusted correctly.
# The 3D printers own z offset might not work using fullcontrol.
 
steps = fc.move(steps, fc.Vector(x=offset_x, y=offset_y, z=offset_z))

# Show the bed / build area size, with the cost of an extra travel move at the start of the gcode.
# Works also without 3d printing
calibration = calibration(bed_x_max = 300, bed_y_max = 300)
steps = calibration+steps

## Move extruder up a set amount (Default = 25) after 3D print is done.
steps.append(fc.Extruder(on=False))
steps.append(fc.Point(z=+Z_hop))

if generate_circle:
    steps.append(fc.PlotAnnotation(label="circle", point=fc.move(circle_centers[0], fc.Vector(x=offset_x, y=offset_y, z=offset_z))))

fc.transform(steps, 'plot', fc.PlotControls(line_width = line_width*10, color_type='print_sequence'))

# Uncomment if you want to 3D print / generate GCODE.
#fc.transform(steps, 'gcode', fc.GcodeControls(save_as='my_design', initialization_data=settings))
