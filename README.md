# fullcontrol-airfoil
This a project that is in a very alpha state so don't except much.

**airfoil.py** file generates NACA airfoils that can be put to a set z height and their chord size can be changed. The program accepts 4 digit naca airfoils with no leading zeroes in them.

**airfoil_loft_vase.py** does the same thing as the airfoil.py except it smooths between the airfoils to create layers. This version does vase mode but at the cost of the bottom of the airfoil being flat and broken. **This version is out of date compared to airfoil_loft.py. If someonew wants to take the airfoil_loft.py and make it vase mode, feel free to.**

**airfoil_loft.py** (not uploaded yet) Takes the base of airfoil.py and creates an average between them to create a wing. The airfoil generation also is working as intended. The next step is to create some kind of infill pattern. See: issue #1

Todo list for everyone:
- [] Issue #1: Infill.
- [] Vase mode implementation for airfoil_loft.py
- [] Code optimization, adding comments and cleaning up the code

Todo list for Aapo:
- [] Basically everything from the other todo list
- [] Answer issue #2


A lot of chatgpt was used in the making of this script. I am slowly editing the worst parts out and it shouldn't be a problem anymore.