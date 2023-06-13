# Fullcontrol-Airfoil

## Overview

Fullcontrol airfoil is a Python script designed to generate 3D printed wings. It's a tool for hobbyists and makers to create custom gcode using [fullcontrol](https://github.com/FullControlXYZ/fullcontrol) for generating wings.

# Installation and Getting Started

Dependencies:
numpy and [fullcontrol](https://github.com/FullControlXYZ/fullcontrol)

To install the depencies, run the commands:

pip install numpy
pip install git+https://github.com/FullControlXYZ/fullcontrol

Run the code after installing the dependencies, using the command: `python3 src/main.py`

To modify the parameters of the airfoil, edit the `main.py` file.

## Usage Examples

## Todo

- [ ] More / better documentation
- [ ] Issue #1 and #3: Wing spars and ribs. (Spars mostly implemented)
- [x] Issue #1: Infill
- [x] Creating elliptical wings.
- [ ] Vase mode implementation
- [ ] A feature to create shapes that remove / add to the wing. For example to make a cutout for a control surface.
- [ ] Issue #9: More infill options. Maybe hexagonal, rectilinear or gyroid?
- [ ] [Add more airfoil generation options](https://en.m.wikipedia.org/wiki/NACA_airfoil)
- [ ] GUI?
- [ ] Mesh generation?

## Parameters

#### Airfoil Parameters

`naca_nums`: NACA airfoil numbers for the NACA airfoil method. `Default:` `['2412', '2412']`.  
`num_points`: Resolution of airfoil. Higher values give better quality but slower performance and larger file size for gcode. `Default:` `128`.

#### Wing Parameters

`z_positions`: Z-coordinates for each airfoil section. `Default:` `[0, 40]`.  
`chord_lengths`: Chord length for each airfoil section. `Default:` `[100, 75]`.

#### File Extraction Parameters
`file_extraction`: Enable to use file extraction, disable for NACA airfoil generation method. `Default:` `False`.  
`filenames`: File names for file extraction method. These have to be in the profiles folder. `Default:` `['naca2412.dat', 'naca2412.dat']`.

#### Infill Parameters
`generate_infill`: Enable to generate infill. `Default:` `True`.  
`infill_density`: Density of infill. Higher values result in denser infill. `Default:` `6`.  
`infill_reverse`: Enable to reverse infill direction. `Default:` `False`.  
`infill_rise`: Enable to raise infill by half layer height when returning to the start point of infill. `Default:` `False`.  
`infill_type`: Infill pattern type. Only option is `modified_triangle_wave_infill`.

## Known Issues and Limitations

1. The script execution may be slow.
2. Only one infill option: `modified_triangle_wave_infill`. There's an [issue](https://github.com/aapolipponen/fullcontrol-airfoil/issues/9) for this.
3. Elliptical wings can only be elliptical from both sides or not at all.
4. Elliptical wing's curvature amount can only be changed for both of the edges.

## Contributions

Contributions to fullcontrol airfoil are welcome and encouraged! If you have an enhancement or a bug fix, feel free to make a pull request.

## License
Fullcontrol airfoil is released under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).