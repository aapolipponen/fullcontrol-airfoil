# fullcontrol-airfoil
This a project that is in a very alpha state so don't except much.

**airfoil.py** file generates NACA airfoils that can be put to a set z height and their chord size can be changed. The program accepts 4 digit naca airfoils with no leading zeroes in them.

**airfoil_loft_vase.py** does the same thing as the airfoil.py except it smooths between the airfoils to create layers. This version does vase mode but at the cost of the bottom of the airfoil being flat and broken. **This version is out of date compared to airfoil_loft.py. If someonew wants to take the airfoil_loft.py and make it vase mode, feel free to.**

**airfoil_loft.py** Takes the base of airfoil.py and creates an average between airfoils if multiple are provided to create a wing. The airfoil generation also is working as intended because the code is much more simpler than the airfoil_loft_vase.py. Other differences between this and airfoil_loft_vase.py are this being a lot more documented, having support for actually printing and not using vase mode. The next step is to create some kind of infill pattern. See: issue #1 And to recreate vase mode for this (An option that can be enabled?). Also making fully filled airfoils (ribs) could be a cool idea if you want to cover the airfoil with film covering to create a very lightweight wing. The wing ribs would need to have a setting for making a hole to pass some kind of support trough them (a spar) that the wing doesn't fall apart.

Todo list for everyone:
- [ ] Issue #1: Infill
- [ ] Issue #1 and #3: Wing spars and ribs.
- [ ] Vase mode implementation for airfoil_loft.py
- [ ] Add more aifoil generation options: https://en.m.wikipedia.org/wiki/NACA_airfoil
- [ ] Code optimization, adding comments and cleaning up the code

Todo list for Aapo:
- [ ] Basically everything from the other todo list
- [ ] Close the Issue #2 27.4



A lot of chatgpt was used in the making of this script. I am slowly editing the worst parts out and it shouldn't be a problem anymore.
