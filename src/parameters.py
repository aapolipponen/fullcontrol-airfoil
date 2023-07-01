from infill_modified_triangle_wave import infill_modified_triangle_wave
import fullcontrol as fc

# Airfoil Parameters
naca_nums = ['2412', '2412'] # NACA airfoil numbers (for NACA airfoil method)
num_points = 128 # Resolution of airfoil - higher values give better quality but slower performance and larger file size for gcode

# Wing Parameters
z_positions = [0, 100]  # Z-coordinates for each airfoil section
chord_lengths = [100, 75]  # Chord length (mm) for each airfoil. May be different scale for extracted airfoils.

# File Extraction Parameters
file_extraction = False # Enable to use file extraction, disable for NACA airfoil method
filenames = ['naca2412.dat', 'naca2412.dat'] # File names for file extraction method. These have to be in the profiles folder.

interpolate=False # Enable if you want to multiply the amount of points the imported airfoil has
interpolate_airfoil_multiplier = 2 # Multiplier for how many times to multiply the amount of points

sort_point_order=True # Sorts the points of the airfoil to start and end at min_X or x=0 depending if you have move_leading_edge enabled or not.
reverse_points_sorting=False # Reverse the direction that sort point order sorts the points to start and end at. If enabled makes the points start and end at max_x or x=chord_length.

# Infill Parameters
generate_infill = False
infill_density = 6 # Density of infill (higher values = denser infill)
infill_reverse = False # Enable to reverse infill direction. Used if file_extraction makes the airfoil start at max x instead of min x.
infill_rise = False # Enable to raise infill by half layer height when returning to start point of infill. Makes the hop from layer to layer smaller.
infill_type = infill_modified_triangle_wave # Infill pattern type

# Fully filled layer
filled_layers_enabled = False
fill_angle = 45
filled_layers = [0, 0.3, 0.6, 24.6, 24.9, 25.2, 49.8, 50.1, 50.4]

# Circle Generation Parameters
generate_circle = False
circle_centers = [ # Center points for start and end of circle
    {"start_center": fc.Point(x=43.8, y=1.35, z=min(z_positions)), "end_center": fc.Point(x=43.8, y=1.35, z=max(z_positions))},
]
circle_radius = 4 # Radius of circle
circle_num_points = 24 # Number of points in circle
circle_offset = 0.75 # Offset for second circle
circle_segment_angle = 45 # Angle covered by each pass when drawing circle
circle_start_angle = 180 # Starting angle for circle. Started on the outer circle.

# Wing Curvature Settings
move_leading_edge = True # Allows movement for the leading edge. If true the edge moves if an chord_length upper in z is smaller.
move_trailing_edge = True # Allows movement for the trailing edge. If true the edge moves if an chord_length upper in z is smaller.

curved_wing = False # Right now uses quadratic interpolation. More options coming soon.
curve_amount = 1 # Ellipse curvature amount (1 = fully curved, 0 = not curved)

# Layer height and width settings

layer_height = 0.3
line_width = 0.4

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

# 3D Printing Configuration
gcode_generation = False # Enable gcode generation.
gcode_name = 'gcode_output' # Output filename for G-code

# Printer Specific Settings
printer_settings = {
    "extrusion_width": line_width, # Width of extrusion in mm
    "extrusion_height": layer_height, # Height of extrusion in mm
    "print_speed": 2000, # Print speed (acceleration)
    "travel_speed": 2000, # Travel speed (acceleration)
    "nozzle_temp": 210, # Nozzle temperature in degrees Celsius
    "bed_temp": 60, # Bed temperature in degrees Celsius
}

# Plot Settings
plot_neat_for_publishing = True # Hides travel moves and the coordinates so the plot is just a 3d view of the airfoil. Used in for example taking images for the documentation.
plot_style = "tube" # Options: "tube" and "line". Tube shows the lines in 3d as, well tubes. The line option shows the lines as 2d lines.

# Debug Settings
print_total_layers = True
print_rendering_plot = True
print_rendering_plot_done = True
print_generating_gcode = True
print_time_taken = True
print_generation_done = True

# SETTINGS END
