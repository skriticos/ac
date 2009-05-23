import transform

"""
Points for half-star polygons extending from 0 to 100 on the abscissa and
from 0 to 180 on the ordinate.
"""
LEFT = (
    (100, 0), #top
    (75, 65), #top2left
    (0, 75), #left
    (50, 115), #left2bottom
    (40, 180), #bottom left
    (100, 140) #bottom middle
    )

(offset_x, offset_y, size_x, size_y) = transform.size(LEFT)

# Points in reverse order!
RIGHT = transform.mirror(LEFT, True, size_x, size_y)

"""
A full star, twice as wide, for auto-closing drawing functions or with a
duplicate line.
"""
STAR = LEFT + transform.move(RIGHT, size_x, 0)[1:-1]

STARLINES = STAR + LEFT[0]

del offset_x, offset_y, size_x, size_y
