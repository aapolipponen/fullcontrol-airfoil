import numpy as np
import fullcontrol as fc
import math
from airfoils import Airfoil

def calibration(bed_x_max, bed_y_max):
    calibration = []
    calibration.append(fc.Extruder(on=False))
    calibration.append(fc.Point(x=bed_x_max, y=bed_y_max, z=10))
    calibration.append(fc.Point(x=0, y=0, z=10))
    calibration.append(fc.Extruder(on=True))
    return calibration

def naca_airfoil(naca_num, num_points, z, chord_length):
    """
    Generates the coordinates of a NACA airfoil at a specific z height and chord length.
    
    Parameters:
        naca_num (str): The NACA airfoil number.
        num_points (int): The number of points to generate.
        z (float): The z-coordinate at which to generate the airfoil.
        chord_length (float): The chord length of the airfoil.
        
    Returns:
        list: A list of fc.Point objects containing the coordinates of the NACA airfoil at the specified z height and chord length.
    """
    x = np.linspace(0, 1, num_points)
    
    if len(naca_num) == 4:
        m = int(naca_num[0]) / 100  # Maximum camber
        p = int(naca_num[1]) / 10   # Location of maximum camber
        t = int(naca_num[2:]) / 100 # Maximum thickness
        
        y_t = 5*t * (0.2969*np.sqrt(x) - 0.126*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
        
        if p == 0 or m == 0:
            yc = np.zeros_like(x)
        else:
            yc = np.where(x < p, m/p**2 * (2*p*x - x**2), m/(1-p)**2 * ((1-2*p) + 2*p*x - x**2))
        
    elif len(naca_num) == 5:
        naca_num = int(naca_num)
        t = (naca_num % 1000) / 100
        m = ((naca_num // 1000) % 100) / 100
        k = (naca_num // 100000) / 100
        
        y_t = (t/0.2) * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1036*x**4)
        yc = (k/0.2) * (0.0580*x**5 - 0.1265*x**4 + 0.3516*x**3 - 0.2843*x**2 + 0.1036*x)
        
    else:
        raise ValueError("Invalid NACA number. Must be 4 or 5 digits long.")

    theta = np.arctan(np.gradient(yc, x))
    xu = x - y_t*np.sin(theta)
    xl = x + y_t*np.sin(theta)
    yu = yc + y_t*np.cos(theta)
    yl = yc - y_t*np.cos(theta)
    
    xu *= chord_length
    yu *= chord_length
    xl *= chord_length
    yl *= chord_length
    
    steps = []
    for i in range(num_points):
        steps.append(fc.Point(x=xu[i], y=yu[i], z=z))
    for i in range(num_points-1, -1, -1):
        steps.append(fc.Point(x=xl[i], y=yl[i], z=z))
    
    return steps

def airfoil_loft(naca_nums, num_points, z_values, chord_lengths, layer_height):
    airfoils = [naca_airfoil(num, num_points, z, chord) for num, z, chord in zip(naca_nums, z_values, chord_lengths)]

    steps = []

    for i, (airfoil1, airfoil2) in enumerate(zip(airfoils[:-1], airfoils[1:])):

        num_layers = int((z_values[i+1] - z_values[i]) / layer_height)

        if num_layers > 0:
            for j in range(num_layers):

                t = j / num_layers

                layer = [fc.Point(x=p1.x*(1-t) + p2.x*t, y=p1.y*(1-t) + p2.y*t, z=p1.z*(1-t) + p2.z*t)
                         for p1, p2 in zip(airfoil1, airfoil2)]

                if i == 0 and j == 0:
                    steps.extend(layer)
                else:
                    steps.append(layer[-1])

                steps.extend(layer[1:] + [layer[0]])

                # Calculate min_x and max_x using the current layer
                min_x = min(point.x for point in layer)
                max_x = max(point.x for point in layer)

                # Apply triangle_wave_infill for the current layer
                steps = triangle_wave_infill(steps, layer[0].z, min_x, max_x)

    return steps

def custom_distance_1d(p1, p2, ignore):
    if ignore == 'x':
        return abs(p1.y - p2.y)
    elif ignore == 'y':
        return abs(p1.x - p2.x)

def find_closest(point, point_list, ignore, condition):
    min_distance = float('inf')
    closest_point = None

    for p in point_list:
        if p.z == point.z:
            if (condition == "greater" and p.y > 0) or (condition == "less" and p.y < 0):
                distance = custom_distance_1d(point, p, ignore)
                if distance < min_distance:
                    min_distance = distance
                    closest_point = p

    return closest_point


def triangle_wave_infill(steps, z, min_x, max_x):
    density = 24
    s_density = max_x / density
        
    for i in range(density-1, 0, -1):  # Invert the max and min values
        added = max_x - s_density * i
        condition = "greater" if i % 2 == 1 else "less"
        coord = fc.Point(x=added, y=None, z=z)
        closest = find_closest(coord, steps, 'y', condition)
        steps.append(closest)

    # Add points to the middle of the shape
    second_last_point = fc.Point(x=min_x + s_density, y=0, z=z)
    last_point = fc.Point(x=min_x, y=0, z=z)

    steps.append(second_last_point)
    steps.append(last_point)
    
    return steps


# SETTINGS
layer_height = 0.3
line_width = 0.4
#These are good settings for my 3d printer. Feel free to change them to your settings. 
#The speed values are kinda high so many printers probably wont handle it.
settings = {
    "extrusion_width": line_width,
    "extrusion_height": layer_height,
    "print_speed": 6000,
    "travel_speed": 8000,
    "nozzle_temp": 220,
    "bed_temp": 55,
}

naca_nums = ['2412', '2412']  # List of NACA airfoil numbers
num_points = 128 # The resolution / accuracy of your airfoil. 
# resolution = graphical quality, generation speed, gcode size (using default settings)
# 1024 = (Dont use this one) Dimishing returns, so slow you don't want to use this one, 22.3 MB
# 512 = (Probably don't want to use this either.) Really nice, really slow, 11,2 MB 
# 256 = Better, somewhat slow, 5.4 MB
# 128 = Default, default, 2.7 MB
# 64 = Worse quality, Fast, 1.3 MB
# 32 = (Dont use this one) Curves look ok but the leading edge is really really bad, Really fast, 0,7 MB 

z_values = [0, 15]  # List of z-values for the airfoils
chord_lengths = [100, 75]  # Chord lengths of the airfoils

# NOTE: If you want to enable 3d printing 
# uncomment the things down after fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence'))

steps = airfoil_loft(naca_nums, num_points, z_values, chord_lengths, layer_height)

# Debug
#print(steps)

# Offset the generated airfoil.
# If 3D printing make sure to double check this,
# because it might be different on different printers and airfoils.
steps = fc.move(steps, fc.Vector(x=50))
steps = fc.move(steps, fc.Vector(y=100))

# Show the bed size, with the cost of an extra travel move at the start of the gcode.
# Works also without 3d printing
calibration = calibration(bed_x_max = 300, bed_y_max = 300)
steps = calibration+steps
    
## Move extruder up a set amount (Default = 25) after 3D print is done.
Z_hop = 25
steps.append(fc.Extruder(on=False))
steps.append(fc.Point(z=+Z_hop))

fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence'))

# Uncomment if you want to 3D print / generate GCODE.
#fc.transform(steps, 'gcode', fc.GcodeControls(save_as='my_design', initialization_data=settings))
