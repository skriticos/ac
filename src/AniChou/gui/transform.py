def size(points):
    """
    Return the extremes of an iterable of points.
    
    (offset_x, offset_y, width, height)
    """
    offset_x = offset_y = size_x = size_y = 0
    for x, y in points:
        # No IF because Python is supposed to reward high-level coding.
        offset_x = min(offset_x, x)
        offset_y = min(offset_y, y)
        size_x = max(size_x, x)
        size_y = max(size_y, y)
    return (offset_x, offset_y, size_x, size_y)

def move(points, offset_x, offset_y):
    """
    Return tuple of the points in an iterable, all moved by the offsets.
    """
    result = []
    for x, y in points:
        result.append((
            x + offset_x,
            y + offset_y
            ))
    return tuple(result)

def scale(figure, width, height, even = False, size_x = 0, size_y = 0):
    """
    Takes an iterable of (x, y) and adjusts them so the biggest x is equal
    to width.
    
    Returns a tuple of tuples.
    
    Forcing proportional scaling does not stretch the figure to fill the
    area.

    If the figure is not cornered at the origin its distance from there
    will be sclaed as well!
    
    Hard-coding the maximum input dimensions saves a little time.
    """
    # TODO optimize the hell out of it.
    if not (size_x and size_y):
        (offset_x, offset_y, size_x, size_y) = size(figure)
    # Calculate factor.
    scale_x = float(width ) / size_x
    scale_y = float(height) / size_y
    # Shrink if necessary.
    if even:
        scale_x = scale_y = min(scale_x, scale_y)
    # Apply.
    result = []
    for x, y in figure:
        # TODO more elegant using map and matrix multiplication.
        result.append((
            int(x * scale_x),
            int(y * scale_y),
            ))
    return tuple(result)

def mirror(figure, reverse = False, size_x = 0, size_y = 0):
    """
    Takes an iterable of (x, y) and mirrors them left to right.
    
    Returns a tuple of tuples.
    
    Optionally reverses the order of the points, so you can concatenate with
    the original to obtain a closed path.
    
    Hard-coding the maximum input dimensions saves a little time.
    """
    if not (size_x and size_y):
        (offset_x, offset_y, size_x, size_y) = size(figure)
    # Calculate center column.
    origin = size_x / 2
    # Apply.
    result = []
    for x, y in figure:
        result.append((
            origin + (origin - x),
            y
            ))
    if reverse:
        result.reverse()
    return tuple(result)
