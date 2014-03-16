from . import core
import logging
import sys
import curses
import os
import copy

class VKeyEvent(object):
    def __init__(self, key_code):
        self._key_code = key_code
        self._accepted = False

    def key(self):
        return chr(self._key_code)

    def keyCode(self):
        return self._key_code

    def keyUnicode(self):
        return unichr(self._key_code)

    def accept(self):
        self._accepted = True

    def accepted(self):
        return self._accepted

class VPainter(object):
    def __init__(self, screen, widget):
        self._screen = screen
        self._widget = widget

    def write(self, x, y, string, fg_color=None, bg_color=None):
        abs_pos = self._widget.mapToGlobal(x, y)
        self._screen.write(abs_pos[0], abs_pos[1], string, fg_color, bg_color)

    def screen(self):
        return self._screen

    def clear(self, x, y, w, h):
        abs_pos = self._widget.mapToGlobal(x, y)
        for h_idx in xrange(h):
            self._screen.write(abs_pos[0], abs_pos[1]+h_idx, ' '*w, 0)

class VScreen(object):
    def __init__(self):
        self._curses_screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()

        self._curses_screen.keypad(1)
        self._curses_screen.nodelay(True)
        self._curses_screen.leaveok(True)
        self._curses_screen.notimeout(True)

        self._initColorPairs()

    def deinit(self):
        curses.nocbreak()
        self._curses_screen.keypad(0)
        curses.echo()
        curses.endwin()

    def leaveok(self, flag):
        self._curses_screen.leaveok(flag)

    def refresh(self):
        self._curses_screen.refresh()

    def size(self):
        y, x = self._curses_screen.getmaxyx()
        return (x,y)

    def getch(self, *args):
        return self._curses_screen.getch(*args)

    def write(self, x, y, string, fg_color=None, bg_color=None):
        size = self.size()
        if x >= size[0] or y >= size[1]:
            return

        if (x+len(string) >= size[0]):
            string = string[:size[0]-x]
            self._curses_screen.addstr(y, x,string[1:], curses.color_pair(self.getColorPair(fg_color, bg_color)))
            self._curses_screen.insstr(y, x, string[0], curses.color_pair(self.getColorPair(fg_color, bg_color)))
        else:
            self._curses_screen.addstr(y,x,string, curses.color_pair(self.getColorPair(fg_color, bg_color)))

    def numColors(self):
        return curses.COLORS

    def supportedColors(self):
        result = []
        for c in xrange(self.numColors()):
             result.append(VColor(curses_rgb=curses.color_content(c), index=c))
        return result

    def getColorPair(self, fg=None, bg=None):
        fg_index = -1 if fg is None else fg.index()
        bg_index = -1 if bg is None else bg.index()

        return self._colormap.index( (fg_index, bg_index) )

    def setCursorPos(self, x, y):
        curses.setsyx(y,x)
        self._curses_screen.move(y,x)
        self.refresh()

    def cursorPos(self):
        pos = self._curses_screen.getyx()
        return pos[1], pos[0]

    def _initColorPairs(self):
        counter = 1
        self._colormap = [ (-1, -1) ]
        for bg in range(0, self.numColors()):
            for fg in range(0, self.numColors()):
                if fg == 0 and bg == 0:
                    continue
                self._colormap.append((fg, bg))
                curses.init_pair(counter, fg, bg)
                counter += 1

class DummyVScreen(object):
    def __init__(self):
        self._cursor_pos = (0,0)
        self._render_output = []
        self._size = (60, 25)
        for h in xrange(self._size[1]):
            row = []
            self._render_output.append(row)
            for w in xrange(self._size[0]):
                row.append(' ')

        self._log = []
        self._log.append("Inited screen")
    def deinit(self):
        self._log.append("Deinited screen")

    def refresh(self):
        self._log.append("Refresh")

    def size(self):
        return self._size

    def cursorPos(self):
        return self._cursor_pos

    def setCursorPos(self, x, y):
        self._cursor_pos = (x,y)

    def leaveok(self, flag):
        pass

    def addstr(self, *args):
        pass

    def getch(self, *args):
        return -1

    def getColor(self, fg, bg):
        return 0

    def write(self, x, y, string, color):
        for pos in xrange(len(string)):
            try:
                self._render_output[y][x+pos] = string[pos]
            except:
                pass

    def dump(self):
        print "+"*(self._size[0]+2)
        for r in self._render_output:
            print "+"+''.join(r)+"+"
        print "+"*(self._size[0]+2)

    def charAt(self, x, y):
        return self._render_output[y][x]

    def stringAt(self, x, y, l):
        return ''.join(self._render_output[y][x:x+l])

class VHLayout(object):
    def __init__(self):
        self._widgets = []
        self._parent = None

    def addWidget(self, widget):
        self._widgets.append(widget)

    def apply(self):
        size = self.parent().size()
        available_size = size[0]/len(self._widgets)
        for i,w in enumerate(self._widgets):
            w.move(available_size*i,0)
            w.resize(available_size, size[1])

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

class VVLayout(object):
    def __init__(self):
        self._widgets = []
        self._parent = None

    def addWidget(self, widget):
        self._widgets.append(widget)

    def apply(self):
        size = self.parent().size()
        available_size = size[1]/len(self._widgets)
        remainder = size[1] % len(self._widgets)
        plot_pos = 0
        for i,w in enumerate(self._widgets):
            w.move(0, plot_pos)
            if remainder > 0:
                w.resize(size[0], available_size+1)
                remainder -= 1
                plot_pos += available_size + 1
            else:
                w.resize(size[0], available_size)
                plot_pos += available_size

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

class VApplication(core.VCoreApplication):
    def __init__(self, argv, screen=None):
        super(VApplication, self).__init__(argv)
        os.environ["ESCDELAY"] = "25"
        if screen:
            self._screen = screen
        else:
            self._screen = VScreen()

        self._top_level_widgets = []
        self._focused_widget = None
        self._palette = self.defaultPalette()

    def exec_(self):
        self.renderWidgets()
        while 1:
            self.processEvents()

    def processEvents(self):
        c = self._screen.getch()
        if c < 0:
            for t in self._timers:
                t.heartbeat()
            self.renderWidgets()
            return
        elif c == 27:
            next_c = self._screen.getch()
            if next_c == -1:
                pass

        event = VKeyEvent(c)
        if self.focusedWidget():
            self.focusedWidget().keyEvent(event)
        self._screen.leaveok(False)
        #self._screen.addch(1,1,c)
        self.renderWidgets()
        # Check if screen was re-sized (True or False)
        x,y = self._screen.size()
        #resize = curses.is_term_resized(y, x)

        # Action in loop if resize is True:
        #if resize is True:
            #x, y = self._screen.size()
            #curses.resizeterm(y, x)
            #self.renderWidgets()

    def exit(self):
        super(VApplication, self).exit()
        self._screen.deinit()

    def addTopLevelWidget(self, widget):
        self._top_level_widgets.append(widget)

    def renderWidgets(self):
        #curpos=self._screen.cursorPos()
        for w in self._top_level_widgets:
            painter = VPainter(self._screen, w)
            w.render(painter)
            #self._screen.setCursorPos(*curpos)
            self._screen.refresh()

    def screen(self):
        return self._screen

    def setFocusWidget(self, widget):
        self._focused_widget = widget

    def focusedWidget(self):
        return self._focused_widget

    def defaultPalette(self):
        palette = VPalette()
        palette.setDefaults()
        return palette

    def palette(self):
        return self._palette

class VWidget(core.VObject):
    def __init__(self, parent=None):
        super(VWidget, self).__init__(parent)
        if parent is None:
            VApplication.vApp.addTopLevelWidget(self)
            self._size = VApplication.vApp.screen().size()
            self.setFocus()
        else:
            self._size = self.parent().size()

        self._pos = (0,0)
        self._layout = None
        self._visible = False
        self._palette = None

    def keyEvent(self, event):
        if not event.accepted():
            self._parent.keyEvent(event)

    def setFocus(self):
        VApplication.vApp.setFocusWidget(self)

    def move(self, x, y):
        self._pos = (x,y)

    def resize(self, w, h):
        self._size = (w,h)

    def pos(self):
        return self._pos

    def size(self):
        return self._size

    def width(self):
        return self._size[0]

    def height(self):
        return self._size[1]

    def show(self):
        self.setVisible(True)

    def hide(self):
        self.setVisible(False)

    def setVisible(self, visible):
        self._visible = visible

    def isVisible(self):
        return self._visible

    def addLayout(self, layout):
        self._layout = layout
        self._layout.setParent(self)

    def setGeometry(self, x, y, w, h):
        self._pos = (x,y)
        min_size = self.minimumSize()
        self._size = (max(min_size[0], w) , max(min_size[1], h))

    def mapToGlobal(self, x, y):
        if self.parent() is None:
            return (x,y)

        global_corner = self.parent().mapToGlobal(0,0)
        return (global_corner[0] + self.pos()[0] + x, global_corner[1] + self.pos()[1] + y)

    def render(self, painter):
        if not self.isVisible():
            return

        if self._layout is not None:
            self._layout.apply()

        for w in self.children():
            child_painter = VPainter(painter.screen(), w)
            w.render(child_painter)

    def palette(self):
        if self._palette is None:
            self._palette = VApplication.vApp.palette().copy()

        return self._palette


class VFrame(VWidget):
    def __init__(self, parent=None):
        super(VFrame, self).__init__(parent)

    def render(self, painter):
        w, h = self.size()
        painter.write(0, 0, '+'+"-"*(w-2)+"+")
        for i in xrange(0, h-2):
            painter.write(0, i+1, '|'+' '*(w-2)+"|")
        painter.write(0, h-1, '+'+"-"*(w-2)+"+")

        super(VFrame, self).render(painter)

class VLabel(VWidget):
    def __init__(self, label, parent=None):
        super(VLabel, self).__init__(parent)
        self._label = label

    def render(self, painter):
        super(VLabel, self).render(painter)
        w, h = self.size()
        fg_color = self.palette().color(VPalette.ColorGroup.Active,
                                        VPalette.ColorRole.WindowText)
        bg_color = self.palette().color(VPalette.ColorGroup.Active,
                                        VPalette.ColorRole.Window)
        for i in xrange(0, h/2):
            painter.write(0, i, ' '*w, fg_color, bg_color)
        painter.write(0, h/2, self._label + ' '*(w-len(self._label)), fg_color, bg_color)
        for i in xrange(1+h/2, h):
            painter.write(0, i, ' '*w, fg_color, bg_color)

    def keyEvent(self, event):
        self._label = self._label + event.key()
        event.accept()

    def minimumSize(self):
        return (len(self._label), 1)

    def setText(self, text):
        self._label = text

class VLineEdit(VWidget):
    def __init__(self, contents="", parent=None):
        super(VLineEdit, self).__init__(parent)
        self._text = contents
        self._cursor_position = len(self._text)
        self._selection = None
        self.returnPressed = core.VSignal(self)
        self.cursorPositionChanged = core.VSignal(self)
        self.textChanged = core.VSignal(self)
        self.selectionChanged = core.VSignal(self)

    def cursorPosition(self):
        return self._cursor_position

    def setCursorPosition(self, position):
        old_pos = self._cursor_position
        self._cursor_position = position
        self.cursorPositionChanged.emit(old_pos, position)

    def setSelection(self, start, length):
        if len(self._text) == 0:
            return
        self._selection = (0, len(self._text))
        self.selectionChanged.emit()

    def selectAll(self):
        if len(self._text) == 0:
            return
        self._selection = (0, len(self._text))
        self.selectionChanged.emit()

    def deselect(self):
        self._selection = None
        self.selectionChanged.emit()

    def home(self):
        self._cursor_position = 0
        self.cursorPositionChanged.emit(old_pos, position)

    def end(self):
        self._cursor_position = len(self._text)
        self.cursorPositionChanged.emit(old_pos, position)

    def text(self):
        return self._text

    def setText(self, text):
        self.deselect()
        self._text = text
        self.textChanged.emit(self._text)

    def backspace(self):
        pass

    def clear(self):
        self.setText("")

    def cursorForward(self, mark):
        pass

    def cursorBackward(self, mark):
        pass

    def minimumSizeHint(self):
        return (1, 1)

    def render(self, painter):
        super(VLineEdit, self).render(painter)
        w, h = self.size()
        painter.write(0, 0, self._text + ' '*(w-len(self._text)), 0)

        VCursor.setPos(self.mapToGlobal(0,0)[0]+self._cursor_position,self.mapToGlobal(0,0)[1])

    def keyEvent(self, event):
        if event.keyCode() == 10:
            self.returnPressed.emit()
        elif event.keyCode() == curses.KEY_LEFT:
            self._cursor_position = max(0, self._cursor_position-1)
        elif event.keyCode() == curses.KEY_RIGHT:
            self._cursor_position = min(len(self._text), self._cursor_position+1)
        elif event.keyCode() == 127:
            self._cursor_position -= 1
            self._cursor_position = max(0, self._cursor_position)
            if self._cursor_position:
                self._text = self._text[:self._cursor_position] + self._text[self._cursor_position+1:]
        else:
            self._text = self._text[:self._cursor_position] + event.key() +  self._text[self._cursor_position:]
            self._cursor_position += 1
        event.accept()

    def minimumSize(self):
        return (1, 1)

class VPushButton(VWidget):
    def __init__(self, label, parent=None):
        super(VPushButton, self).__init__(parent)
        self._label = label

    def render(self, painter):
        super(VPushButton, self).render(painter)
        for i in xrange(0, h/2):
            painter.write(0, i, ' '*w)
        painter.write(0, h/2, "[ "+self._label + " ]"+ ' '*(w-len(self._label)-4))
        for i in xrange(1+h/2, h):
            painter.write(0, i, ' '*w)

class VTabWidget(VWidget):
    def __init__(self, parent=None):
        super(VTabWidget, self).__init__(parent)
        self._tabs = []
        self._selected_tab_idx = -1

    def addTab(self, widget, label):
        self._tabs.append((widget, label))
        self._selected_tab_idx = 2

    def render(self, screen):
        screen = VApplication.vApp.screen()
        w, h = screen.size()
        if len(self._tabs):
            tab_size = w/len(self._tabs)
            header = ""
            for index, (_, label) in enumerate(self._tabs):
                header = label+" "*(tab_size-len(label))
                screen.write(tab_size * index, 0, header, curses.color_pair(1 if index == self._selected_tab_idx else 0))
            widget = self._tabs[self._selected_tab_idx][0]
            widget.render(screen)

class VCursor(object):
    @staticmethod
    def setPos(x,y):
        VApplication.vApp.screen().setCursorPos(x,y)

    def pos(x,y):
        return VApplication.vApp.screen().cursorPos(x,y)

class VColor(object):
    def __init__(self, rgb=None, curses_rgb=None, index=None):
        if rgb is None and curses_rgb is None and index is None:
            raise Exception("Unspecified color")

        self._rgb = rgb
        self._curses_rgb = curses_rgb
        self._index = index

    def cursesRgb(self):
        if self._curses_rgb is None:
            if self._rgb is not None:
                self._curses_rgb = VColor.rgbToCursesRgb(self._rgb)
            elif self._index is not None:
                self._curses_rgb = VApplication.vApp.screen().supportedColors()[self._index].cursesRgb()
            else:
                raise Exception("Not supposed to reach this")

        return self._curses_rgb

    def rgb(self):
        if self._rgb is None:
            if self._curses_rgb is not None:
                self._rgb = VColor.cursesRgbToRgb(self._curses_rgb)
            elif self._index is not None:
                self._rgb = VApplication.vApp.screen().supportedColors()[self._index].rgb()
            else:
                raise Exception("unreachable")

        return self._rgb

    def hexString(self):
        return "%0.2X%0.2X%0.2X" % self.rgb()

    def index(self):
        if self._index is None:
            self._index = self._lookupIndex()

        return self._index

    def _lookupIndex(self):
        supported_colors = VApplication.vApp.screen().supportedColors()

        closest = sorted([(color.distance(self), color) for color in supported_colors], key=lambda x: x[0])[0]

        return closest[1].index()

    def r(self):
        return self.rgb()[0]
    def g(self):
        return self.rgb()[1]
    def b(self):
        return self.rgb()[2]

    def distance(self, other):
        return (self.r() - other.r())**2 + (self.g() - other.g())**2 + (self.b() - other.b())**2


    @staticmethod
    def cursesRgbToRgb(curses_rgb):
        return tuple([int(x/1000.0 * 255) for x in curses_rgb ])

    @staticmethod
    def rgbToCursesRgb(rgb):
        return tuple([int(x/255 * 1000) for x in rgb ])

class VPalette(object):
    class ColorGroup(object):
        Active, Disabled, Inactive = range(3)

    class ColorRole(object):
        WindowText, \
        Button, \
        Light, \
        Midlight, \
        Dark, \
        Mid, \
        Text, \
        BrightText, \
        ButtonText, \
        Base, \
        Window, \
        Shadow, \
        Highlight, \
        HighlightedText, \
        Link, \
        LinkVisited, \
        AlternateBase, \
        NoRole, \
        ToolTipBase, \
        ToolTipText = range(20)

    def __init__(self):
        self._colors = {}

    def color(self, color_group, color_role):
        return self._colors[(color_group, color_role)]

    def setDefaults(self):
        self._colors = {
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.WindowText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Button) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Light) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Midlight) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Dark) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Mid) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Text) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.BrightText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.ButtonText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Base) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Window) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Shadow) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Highlight) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.HighlightedText) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.Link) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.LinkVisited) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.AlternateBase) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.NoRole) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.ToolTipBase) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Active, VPalette.ColorRole.ToolTipText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.WindowText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Button) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Light) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Midlight) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Dark) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Mid) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Text) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.BrightText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.ButtonText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Base) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Window) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Shadow) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Highlight) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.HighlightedText) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.Link) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.LinkVisited) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.AlternateBase) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.NoRole) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.ToolTipBase) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Disabled, VPalette.ColorRole.ToolTipText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.WindowText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Button) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Light) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Midlight) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Dark) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Mid) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Text) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.BrightText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.ButtonText) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Base) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Window) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Shadow) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Highlight) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.HighlightedText) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.Link) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.LinkVisited) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.AlternateBase) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.NoRole) : VColor( rgb = (255,255,255)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.ToolTipBase) : VColor( rgb = (0,0,0)),
            ( VPalette.ColorGroup.Inactive, VPalette.ColorRole.ToolTipText) : VColor( rgb = (255,255,255))
            }

    def copy(self):
        return copy.deepcopy(self)
