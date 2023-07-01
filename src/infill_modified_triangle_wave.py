import fullcontrol as fc

def find_closest(point, point_list, condition):
    min_distance = float('inf')
    closest_point = None

    for p in point_list:
        # Check if p has a 'z' attribute before trying to access it. Done because of fc.travel_to.
        if hasattr(p, 'z') and p.z == point.z and ((condition and p.y > 0) or (not condition and p.y < 0)):
            distance = abs(point.x - p.x)
            if distance < min_distance:
                min_distance = distance
                closest_point = p

    return closest_point

def add_step(steps, added, z, condition, direction):
    closest = find_closest(fc.Point(x=added, y=None, z=z), steps, condition)
    if direction:
        steps.append(closest if closest and closest.y <= 0 else fc.Point(x=added, y=0, z=z))
    else:
        steps.append(closest if closest and closest.y >= 0 else fc.Point(x=added, y=0, z=z))
    return steps

def infill_modified_triangle_wave(steps, z, min_x, max_x, infill_density, infill_reverse, layer_height, infill_rise):
    s_density = max_x / infill_density

    if infill_reverse:
        for i in range(infill_density - 1, 0, -1):
            added = s_density * i
            condition = (i+1) % 2 == 0  # Shift condition for second half to meet the first half at y=0.
            steps = add_step(steps, added, z, condition, False)

        steps.append(fc.Point(x=min_x, y=0, z=z))

        for i in range(1, infill_density):
            added = s_density * i
            condition = i % 2 == 0  # Maintain original condition for first half
            steps = add_step(steps, added, z, condition, True)

        steps.append(fc.Point(x=max_x, y=0, z=z))
    else:
        for i in range(1, infill_density):
            added = s_density * i
            condition = i % 2 == 0  # Maintain original condition for first half
            steps = add_step(steps, added, z, condition, True)
            
        steps.append(fc.Point(x=max_x, y=0, z=z))
            
        for i in range(infill_density - 1, 0, -1):
            added = s_density * i
            condition = (i+1) % 2 == 0  # Shift condition for second half to meet the first half at y=0.
            steps = add_step(steps, added, z, condition, False)

    if infill_rise:
        steps.append(fc.Point(x=min_x, y=0, z=z+layer_height/2))
    else:
        steps.append(fc.Point(x=min_x, y=0, z=z))

    return steps
