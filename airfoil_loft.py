import numpy as np
import fullcontrol as fc
import math

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

    return steps

# Example usage
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

naca_nums = ['4412', '2412']  # List of NACA airfoil numbers
num_points = 128  # The resolution / accuracy of your airfoil. 512 = Beatiful, slow 256 = 
z_values = [0, 40]  # List of z-values for the airfoils
chord_lengths = [100, 75]  # Chord lengths of the airfoils

#NOTE: If you want to enable 3d printing 
# uncomment the things down after fc.transform(steps, 'plot', fc.PlotControls(line_width=0.6, color_type='print_sequence'))

steps = airfoil_loft(naca_nums, num_points, z_values, chord_lengths, layer_height)


# Offset the generated airfoil.
# If 3D printing make sure to double check this,
# because it might be different on different printers and airfoils.
steps = fc.move(steps, fc.Vector(x=50))
steps = fc.move(steps, fc.Vector(y=100))

# Show the bed size, with the cost of an extra travel move at the start of the gcode.
# Works also without 3d printing
calibration = calibration(bed_x_max = 300, bed_y_max = 300)
steps = calibration+steps
     
# Move extruder up a set amount (Default = 25) after 3D print is done.
Z_hop = 25
steps.append(fc.Extruder(on=False))
steps.append(fc.Point(x=0, y=0, z=+Z_hop))

fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence'))

# Uncomment if you want to 3D print.
#fc.transform(steps, 'gcode', fc.GcodeControls(save_as='my_design', initialization_data=settings)
