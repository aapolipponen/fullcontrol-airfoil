# fullcontrol-airfoil

**airfoil.py** file generates NACA airfoils that can be put to a set z height and their chord size can be changed. The program accepts 4 digit naca airfoils with no leading zeroes in them.

**airfoil_loft.py** Takes the base of airfoil.py and creates an average between airfoils if multiple are provided to create a wing. The airfoil generation also is working as intended because the code is much more simpler than the airfoil_loft_vase.py. Other differences between this and airfoil_loft_vase.py are this being a lot more documented, having support for actually printing and not using vase mode. The next step is to create some kind of infill pattern. See: issue #1 And to recreate vase mode for this (An option that can be enabled?). Also making fully filled airfoils (ribs) could be a cool idea if you want to cover the airfoil with film covering to create a very lightweight wing. The wing ribs would need to have a setting for making a hole to pass some kind of support trough them (a spar) that the wing doesn't fall apart. 3D printing is supported in this version. If you want to create a singlar / single layer airfoil, put the layer height to the second z value. The airfoil.py accepts single airfoils but doesn't support 3D printing.

**airfoil_loft_infill.py** Same as airfoil_loft.py but has infill. The infill is a triangle wave going between the two sides of the airfoil and moving in x by a set amount defined by the infill_density variable. If the infill_density variable is bigger, then the code creates more triangles in that take less x space. And if the infill_density is smaller, then the code creates less triangles that take more x space.

Todo list for everyone:
- [ ] Issue #1 and #3: Wing spars and ribs.
- [ ] Vase mode implementation for airfoil_loft.py
- [ ] Issue #1: Infill
- [ ] [Add more airfoil generation options](https://en.m.wikipedia.org/wiki/NACA_airfoil)
- [ ] Code optimization, adding comments and cleaning up the code




A lot of chatgpt was used in the making of this script. I am slowly editing the worst parts out and it shouldn't be a problem anymore.
