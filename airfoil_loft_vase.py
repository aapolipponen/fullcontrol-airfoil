import numpy as np
import fullcontrol as fc
import math

def naca_airfoil(naca_num, num_points, z, chord_length):
    """
    Generates the coordinates of a NACA airfoil at a specific z height and chord length.
    
    Parameters:
        naca_num (str): The four-digit NACA airfoil number.
        num_points (int): The number of points to generate.
        z (float): The z-coordinate at which to generate the airfoil.
        chord_length (float): The chord length of the airfoil.
        
    Returns:
        list: A list of fc.Point objects containing the coordinates of the NACA airfoil at the specified z height and chord length.
    """
    m = int(naca_num[0]) / 100  # Maximum camber
    p = int(naca_num[1]) / 10   # Location of maximum camber
    t = int(naca_num[2:]) / 100 # Maximum thickness
    
    x = np.linspace(0, 1, num_points)
    y_c = np.zeros_like(x)
    y_t = 5*t * (0.2969*np.sqrt(x) - 0.126*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
    
    # Calculate camber line and upper/lower surfaces
    if p == 0 or m == 0:
        yc = np.zeros_like(x)
        xu = x
        xl = x
    else:
        yc = np.where(x < p, m/p**2 * (2*p*x - x**2), m/(1-p)**2 * ((1-2*p) + 2*p*x - x**2))
        theta = np.arctan(np.gradient(yc, x))
        xu = x - y_t*np.sin(theta)
        xl = x + y_t*np.sin(theta)
    
    yu = yc + y_t*np.cos(theta)
    yl = yc - y_t*np.cos(theta)
    
    # Adjust the calculation of the lower surface
    yl = yc - y_t*np.cos(theta)
    
    # Scale coordinates based on chord length
    xu *= chord_length
    yu *= chord_length
    xl *= chord_length
    yl *= chord_length
    
    # Generate fc.Point objects
    steps = []
    for i in range(num_points):
        steps.append(fc.Point(x=xu[i], y=yu[i], z=z))
    for i in range(num_points-1, -1, -1):
        steps.append(fc.Point(x=xl[i], y=yl[i], z=z))
    
    return steps

def airfoil_loft(naca_nums, num_points, z_values, chord_lengths, layer_height):
    """
    Generates a loft between a series of NACA airfoils at different heights and chord lengths.
    
    Parameters:
        naca_nums (list): A list of the four to six digit NACA airfoil numbers.
        num_points (int): The number of points to generate for each airfoil.
        z_values (list): A list of z-values for the airfoils.
        chord_lengths (list): A list of chord lengths for the airfoils.
        layer_height (float): The height of the layers in the loft.
        
    Returns:
        list: A list of fc.Point objects containing the coordinates of the loft.
    """
    
    # Generate airfoils at different heights using the given NACA numbers, number of points, z-values, and chord lengths
    # and store them in a list called airfoils
    airfoils = [naca_airfoil(num, num_points, z, chord) for num, z, chord in zip(naca_nums, z_values, chord_lengths)]
    
    # Create layers between adjacent airfoils and store them in a list called steps
    steps = []
    
    # Iterate over the pairs of adjacent airfoils
    for i, (airfoil1, airfoil2) in enumerate(zip(airfoils[:-1], airfoils[1:])):
        
        # Determine the number of layers between the current and the next airfoil based on the layer height
        num_layers = int((z_values[i+1] - z_values[i]) / layer_height)
        
        # Iterate over the layers between the current and the next airfoil
        for j in range(num_layers):
            
            # Determine the interpolation factor (t) for the current layer
            t = j / num_layers
            
            # Create a list of points for the current layer by linearly interpolating between the points of the two
            # adjacent airfoils based on the interpolation factor t and the z-value of the current layer
            layer = [fc.Point(x=(1-t)*p1.x + t*p2.x, y=(1-t)*p1.y + t*p2.y, z=z_values[i] + j*layer_height)
                     for p1, p2 in zip(airfoil1, airfoil2)]
            
            # Add the points of the current layer to the list of steps
            steps.extend(layer)
    
    # Return the list of points representing the loft
    return steps

# Example usage
naca_nums = ['4412', '23012', '2412']  # List of NACA airfoil numbers
num_points = 128
z_values = [0, 10, 15]  # List of z-values for the airfoils
chord_lengths = [50, 45, 35]  # Chord lengths of the airfoils
layer_height = 0.2
steps = airfoil_loft(naca_nums, num_points, z_values, chord_lengths, layer_height)
fc.transform(steps, 'plot', fc.PlotControls(line_width=4, color_type='print_sequence'))
