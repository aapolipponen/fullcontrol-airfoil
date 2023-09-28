import time
start = time.time()
import numpy as np
import fullcontrol as fc
from infill_modified_triangle_wave import infill_modified_triangle_wave
from circle_utils import create_circles
from full_fill import fill_shape
from parameters import *

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
        raise ValueError("Invalid NACA number. Must be 4 or 3 digits long. See: https://en.m.wikipedia.org/wiki/NACA_airfoil#Four-digit_series for formatting.")
    m = int(naca_num[0]) / 100
    p = int(naca_num[1]) / 10
    t = int(naca_num[2:]) / 100
    x = np.linspace(0, 1, num_points)
    y_t = 5 * t * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    if p == 0:
        yc = np.zeros_like(x)
    else:
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

def airfoil_extract(chord_length, filename):
    airfoil = []
    with open("profiles/" + filename, 'r') as file:
        lines = file.readlines()
    for line in lines[1:]:
        x, y = map(float, line.split())
        airfoil.append(fc.Point(x=x * chord_length, y=y * chord_length, z=0))
    if interpolate:
        airfoil = optimize_airfoil(airfoil)
    if sort_point_order:
        airfoil = sort_points(airfoil, reverse_points_sorting)
    return airfoil

def optimize_airfoil(airfoil):
    new_points = []
    for i in range(len(airfoil) - 1):
        point1 = airfoil[i]
        point2 = airfoil[i + 1]

        avg_values = [(val1 + val2) / 2 for val1, val2 in zip((point1.x, point1.y, point1.z), (point2.x, point2.y, point2.z))]
        new_point = fc.Point(x=avg_values[0], y=avg_values[1], z=avg_values[2])

        new_points.append(point1)
        new_points.extend([new_point]*interpolate_airfoil_multiplier)

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
                # Quadratic interpolation
                chord_length = chord_lengths[i] + chord_length_diff * (t**2) * curve_amount
            else:
                # Linear interpolation
                chord_length = chord_lengths[i] + chord_length_diff * t 
                
            airfoil = airfoil_wrapper([naca_nums[i]], num_points, [z], [chord_length], file_extraction, [filenames[i]])[0]
                                                           
            # Move airfoil based on chord lengths if edge is not set as straight
            # Calculating these in a different way leads to a weird bug where the infill spills out.
            # For now this method works.
	    # Also has a bug that makes moving imported airfoils impossible.
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
                if infill_type == infill_modified_triangle_wave:
                    layer.extend(infill_modified_triangle_wave(layer, z, min_x, max_x, infill_density, infill_reverse, layer_height, infill_rise))            
            
            if generate_circle and not z in filled_layers:
                layer.extend(create_circles(circle_centers, circle_radius, circle_offset, circle_num_points, circle_start_angle, circle_segment_angle, z))

            # Validate z to ensure it's a multiple of layer_height, if not round to the nearest multiple. Used for the fill_layer
            remainder = z % layer_height
            if remainder != 0:
                if remainder >= layer_height / 2:
                    z += layer_height - remainder
                else:
                    z -= remainder
                    
            # Check if this z-value should be a fully filled layer
            if filled_layers_enabled and z in filled_layers:
                layer.extend(fill_shape(airfoil, line_width, fill_angle, z))

            # After completing the layer, move to next layer using fc.travel_to.
            steps.extend(fc.travel_to(fc.Point(x=min_x, y=0, z=z+layer_height)))
            
            steps.extend(layer)
    
    return steps

steps = loft_shapes()

if offset_wing:
    steps = fc.move(steps, fc.Vector(x=offset_x, y=offset_y, z=offset_z))

if calibration_moves:
    calibration = calibration(bed_x_max, bed_y_max)
    steps = calibration+steps

if z_hop_enabled:
    steps.append(fc.Extruder(on=False))
    steps.append(fc.Point(z=+z_hop_amount))

if gcode_generation:
    if print_generating_gcode:
        print("Generating gcode")
    fc.transform(steps, 'gcode', fc.GcodeControls(save_as=gcode_name, initialization_data=printer_settings))

if print_rendering_plot:
    print("Rendering plot")
    if plot_neat_for_publishing:
        fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence', style=plot_style, neat_for_publishing = True, zoom = 0.8, hide_travel=True, line_width=10))
    else: 
        fc.transform(steps, 'plot', fc.PlotControls(color_type='print_sequence', style=plot_style))

if print_rendering_plot_done:
    print("Rendering done")

if print_time_taken:
    end = time.time()
    time_to_generate = end-start
    print('Generated in: '+str(round(time_to_generate, 3))+' s')
