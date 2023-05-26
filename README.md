# fullcontrol-airfoil

Generates NACA airfoils that can be put to a set z height and their chord size can be changed. The program accepts 4 digit naca airfoils.
Creates an average between airfoils to create a wing. Making fully filled airfoils (ribs) could be a cool idea if you want to cover the airfoil with film covering to create a very lightweight wing. The wing ribs would need to have a setting for making a hole to pass some kind of support trough them (a spar) that the wing doesn't fall apart. If you want to create a singular / single layer airfoil, put the layer height to the second z value. The airfoil.py accepts single airfoils but doesn't support 3D printing.
The infill is a triangle wave going between the two sides of the airfoil and moving in x by a set amount defined by the infill_density variable. If the infill_density variable is bigger, then the code creates more triangles in that take less x space. And if the infill_density is smaller, then the code creates less triangles that take more x space.
Circles are now able to be placed at any coordinates with any radiuses. This can be used to add for example a space to put a carbon fiber rod for making the wing more durable. Infill options other than modified infill_triangle are broken at the moment.

Todo list:
- [ ] More documentation
- [ ] Issue #1 and #3: Wing spars and ribs. (Spars partly implemented.) Ribs proved to be a bit hard. Still probably going to do that pretty soom.
- [ ] Issue #1: Infill
- [ ] Creating elliptical wings. (Partly done)
- [ ] Vase mode implementation
- [ ] [Add more airfoil generation options](https://en.m.wikipedia.org/wiki/NACA_airfoil)
- [ ] Code optimization, adding comments and cleaning up the code