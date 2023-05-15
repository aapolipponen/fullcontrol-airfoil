# fullcontrol-airfoil

**airfoil.py** file generates NACA airfoils that can be put to a set z height and their chord size can be changed. The program accepts 4 digit naca airfoils.

**airfoil_loft.py** Takes the base of airfoil.py and creates an average between airfoils if multiple are provided to create a wing. The airfoil generation also is working as intended because the code is much more simpler than the airfoil_loft_vase.py. The next step is to create some kind of infill pattern. See: issue #1 And to recreate vase mode for this (An option that can be enabled?). Also making fully filled airfoils (ribs) could be a cool idea if you want to cover the airfoil with film covering to create a very lightweight wing. The wing ribs would need to have a setting for making a hole to pass some kind of support trough them (a spar) that the wing doesn't fall apart. 3D printing is supported in this version. If you want to create a singular / single layer airfoil, put the layer height to the second z value. The airfoil.py accepts single airfoils but doesn't support 3D printing.

**airfoil_loft_infill.py** Same as airfoil_loft.py but has infill. The infill is a triangle wave going between the two sides of the airfoil and moving in x by a set amount defined by the infill_density variable. If the infill_density variable is bigger, then the code creates more triangles in that take less x space. And if the infill_density is smaller, then the code creates less triangles that take more x space.

**airfoil_loft_infill_beta.py** Same as airfoil_loft_infill.py, but added importing airfoils, put the project into different scripts and neatened up the settings part. Multithreading is also in testing and already pushed. (Only improved the time by few seconds on a large 30 second wing. Not sure if it will be kept because of code simplicity.) Also circles are now able to be placed at any coordinates with any radiuses. This can be used to add for example a space to put a carbon fiber rod for making the wing more durable. Infill options other than infill_triangle are broken at the moment.

Todo list:
- [ ] Creating elliptical wings.
- [ ] Issue #1 and #3: Wing spars and ribs. (Spars partly implemented.) Ribs proved to be a bit hard. Still probably going to do that pretty soom.
- [ ] Issue #1: Infill
- [ ] Vase mode implementation
- [ ] [Add more airfoil generation options](https://en.m.wikipedia.org/wiki/NACA_airfoil)
- [ ] Code optimization, adding comments and cleaning up the code




A lot of chatgpt was used in the making of this script. I am slowly editing the worst parts out and it shouldn't be a problem anymore.
