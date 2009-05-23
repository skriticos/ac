# Standard.
import math
# Third party.
import wx
# Our own.
import star
import transform

# Integer.
myEVT_LEVEL_CHANGE = wx.NewEventType()
# Binder.
EVT_LEVEL_CHANGE = wx.PyEventBinder(myEVT_LEVEL_CHANGE, 1)

def _paintActive(dc, *xywh):
    c1 = '#72BE2E'
    c2 = '#C9EAAD'
    dc.GradientFillLinear(xywh, c1, c2, nDirection = wx.SOUTH)

def _paintInctive(dc, *xywh):
    c1 = '#ADADAD'
    c2 = '#D5D5D5'
    dc.GradientFillLinear(xywh, c1, c2, nDirection = wx.SOUTH)

class LevelIndicator(wx.Panel):
    """
    A horizontal bar representing a value.
    
    Public writeable attributes:
    
    maximum     Integer represented by a full bar.
    current     Current value as int. Zero for an empty bar.
    editable    Boolean signifying whether mouse interaction modifies current.
    expand      True causes stretching to fill all of our area.
                Only applicable to subclasses.

    After changing values you should call self.Refresh() to redraw.
    """
    DIMENSIONS = 1, 1
    
    def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
        size = wx.DefaultSize):

        wx.Panel.__init__(self, parent, id, pos, size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        self.maximum = 3
        self.current = 2
        self.editable = False
        self.expand = True
    
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        width, height = self.GetClientSizeTuple()
        # Divide by zero.
        segment = width / self.maximum

        active = self.current * segment
        _paintActive(dc, 0, 0, active, height)
        _paintInctive(dc, active, 0, width - active, height)
        # Use wx.Colour with alpha for lighting.

    def ScaledDimensions(self):
        """
        Takes the unscaled size of one undistorted segment image.
        
        Returns the scaled size for one segment.
        """
        size_x, size_y = self.DIMENSIONS
        width, height = self.GetClientSizeTuple()

        segment = width / self.maximum
        scale_x = float(segment) / size_x
        scale_y = float(height) / size_y

        if self.expand:
            return segment, height
        elif scale_x * size_y > height:
            return int(scale_y * size_x), height
        elif scale_y * size_x > segment:
            return segment, int(scale_x * size_y)
 
    def OnMouseEvent(self, event):
        if not self.editable:
            pass
        elif event.LeftIsDown():
            segment, height = self.ScaledDimensions()
            x, y = event.GetPositionTuple()
            # Only if cursor really in stars.
            if y <= height:
                # Number of segments.
                maybe, active = math.modf(float(x) / segment)
                # Both are floats.
                active = int(active)
                if maybe > 0.33:
                    active += 1
                if active > self.maximum:
                    active = self.maximum
                if active != self.current:
                    self.current = active
                    # TODO custom event class storing new value.
                    evt = wx.PyCommandEvent(myEVT_LEVEL_CHANGE, self.GetId())
                    self.GetEventHandler().ProcessEvent(evt)
                self.Refresh()
        event.Skip()

class StarIndicator(LevelIndicator):
    # TODO optionally allow stars to distribute instead of left-align.

    DIMENSIONS = transform.size(star.STAR)[2:]

    def PaintShapes(self, polygons):
        dc = wx.PaintDC(self)
        segment, height = self.ScaledDimensions()
        dc.SetBrush(wx.Brush('#808080'))
        dc.SetPen(wx.Pen('#808080', 1))
        for i, shape in enumerate(polygons):
            points = transform.scale(shape, segment, height, not self.expand,
                *self.DIMENSIONS)
            dc.DrawPolygon(points, segment * i, 0)

    def OnPaint(self, event):
        self.PaintShapes([star.STAR] * self.current)

class HalfStarIndicator(StarIndicator):
    DIMENSIONS = transform.size(star.LEFT)[2:]

    def OnPaint(self, event):
        shapes = []
        for i in range(self.current):
            shapes.append((star.LEFT, star.RIGHT)[i % 2])
        self.PaintShapes(shapes)
