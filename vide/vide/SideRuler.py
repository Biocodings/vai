from videtoolkit import gui, core, utils
import math

class SideRuler(gui.VWidget):
    def __init__(self, parent):
        super(SideRuler, self).__init__(parent)
        self._start = 1
        self._end = None
        self._skip_intervals = []
        self._badges = {}

    def paintEvent(self, event):
        w, h = self.size()
        painter = gui.VPainter(self)
        painter.clear( (0, 0, w, h) )
        num_digits = self._lineNumberWidth()
        entries = _computeLineValues(self._start, h, self._skip_intervals)
        for i, current in enumerate(entries):
            badge_mark = " "
            border = " "
            if self._end is not None and current > self._end:
                painter.write( (0, i), "~".ljust(num_digits)+" "+border,
                                fg_color=gui.VGlobalColor.blue,
                )
                continue

            badge = self._badges.get(current)
            if badge is not None:
                badge_mark = badge.mark()
                bg_color = gui.VGlobalColor.red
            else:
                bg_color = gui.VGlobalColor.blue

            painter.write( (0, i), str(current).rjust(num_digits) + badge_mark + border,
                            fg_color=gui.VGlobalColor.cyan, bg_color=bg_color)

#    def _computeExpectedValues(self):
#        if self._end_line is None:
#            values = range(self._start_line, self._start_line+self.height())
#        else:
#            values = range(self._start_line, min(self._end_line, self._start_line+self.height()))

    def setStart(self, start):
        self._start = start
        self.update()

    def minimumSize(self):
        return (self._lineNumberWidth(), 1)

    def _lineNumberWidth(self):

#        if self._document_model.numLines() == 0:
#            return 1
#
        num_digits = int(math.log10(max(_computeLineValues(self._start, self.height(), self._skip_intervals))))+1
        return num_digits


    def addBadge(self, line, badge):
        self._badges[line] = badge
        self.update()
def _computeLineValues(start, how_many, skip):
    result = []
    current = start
    for i in xrange(how_many):
        for interval in skip:
            begin, end = interval
            if begin < current < end:
                current = end
        result.append(current)
        current += 1
    return result

