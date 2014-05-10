import vixtk
from vixtk import gui, core, utils
from .EditAreaController import EditAreaController
from .positions import CursorPos, DocumentPos
from . import flags
import logging

from pygments.formatter import Formatter
from pygments import token

TOKEN_TO_COLORS = {
    token.Keyword: (gui.VGlobalColor.yellow, None),
    token.Keyword.Namespace: (gui.VGlobalColor.magenta, None),
    token.Comment: (gui.VGlobalColor.cyan, None),
    token.Name.Function: (gui.VGlobalColor.cyan, None),
    token.Name.Class: (gui.VGlobalColor.cyan, None),
}

class EditArea(gui.VWidget):
    debug = logging.INFO
    def __init__(self, parent):
        super().__init__(parent)

        self._controller = EditAreaController(self)

        self._buffer = None
        self._editor_model = None
        self._visual_cursor_pos = (0,0)
        self.setFocusPolicy(vixtk.FocusPolicy.StrongFocus)

        #self.scrollDown = core.VSignal(self)
        #self.scrollDown.connect(self.scrollDownSlot)
        #self.scrollUp = core.VSignal(self)
        #self.scrollUp.connect(self.scrollUpSlot)

        self.cursorPositionChanged = core.VSignal(self)

    def setModels(self, buffer, editor_model):
        self._buffer = buffer
        self._editor_model = editor_model
        self._controller.setModels(buffer, editor_model)
        self.update()

    def _hasModels(self):
        return self._buffer and self._editor_model

    def paintEvent(self, event):
        self.logger.info("XXX paintEvent")
        w, h = self.size()
        painter = gui.VPainter(self)
        painter.erase()
        pos_at_top = self._buffer.viewModel().documentPosAtTop()
        document_cursor_pos = self._buffer.documentCursor().pos()
        if self._hasModels():
            for i in range(0, h):
                document_line = pos_at_top[0] + i
                if document_line <= self._buffer.document().numLines():
                    line = self._buffer.document().getLine(document_line)
                    painter.drawText( (0, i), line.replace('\n', ' '))
                    char_meta = self._buffer.document().charMeta(document_line)
                    colors = [TOKEN_TO_COLORS.get(tok, (None, None)) for tok in char_meta.get("lextoken", [])]
                    painter.setColors( (0,i), colors)

        document_cursor_pos = self._buffer.documentCursor().pos()
        self._setVisualCursorPos( (document_cursor_pos[1]-pos_at_top[1], document_cursor_pos[0]-pos_at_top[0] ))
        #gui.VCursor.setPos( self.mapToGlobal((self._visual_cursor_pos[0], self._visual_cursor_pos[1])))

    def _setVisualCursorPos(self, cursor_pos):
        pos_x = utils.clamp(cursor_pos[0], 0, self.width()-1)
        pos_y = utils.clamp(cursor_pos[1], 0, self.height()-1)
        self._visual_cursor_pos = (pos_x, pos_y)
        gui.VCursor.setPos(self.mapToGlobal((pos_x, pos_y)))

    def scrollDown(self):
        if not self._hasModels():
            return
        top_pos = self._buffer.viewModel().documentPosAtTop()
        if top_pos[0] + self.height() > self._buffer.document().numLines():
            return
        new_pos = (top_pos[0]+1, top_pos[1])
        self._buffer.viewModel().setDocumentPosAtTop(new_pos)
        self.update()

    def scrollUp(self):
        if not self._hasModels():
            return
        top_pos = self._buffer.viewModel().documentPosAtTop()
        if top_pos[0] == 1:
            return

        new_pos = (top_pos[0]-1, top_pos[1])
        self._buffer.viewModel().setDocumentPosAtTop(new_pos)
        self.update()

    def keyEvent(self, event):
        if not self._hasModels():
            return
        self._controller.handleKeyEvent(event)
        self.update()

    def focusInEvent(self, event):
        if not self._hasModels():
            return
        gui.VCursor.setPos(self.mapToGlobal((self._visual_cursor_pos[0], self._visual_cursor_pos[1])))

    def handleDirectionalKey(self, event):
        if not self._hasModels():
            return

        if self._buffer.document().isEmpty():
            return

        key = event.key()

        direction = { vixtk.Key.Key_Up: flags.UP,
                      vixtk.Key.Key_Down: flags.DOWN,
                      vixtk.Key.Key_Left: flags.LEFT,
                      vixtk.Key.Key_Right: flags.RIGHT
                    }[key]

        self.moveCursor(direction)

    def moveCursor(self, direction):
        logging.error("Hello" + str(self._visual_cursor_pos))
        doc_cursor = self._buffer.documentCursor()
        if direction == flags.UP:
            if self._visual_cursor_pos[1] == 0:
                self.scrollUp()
            doc_cursor.toLinePrev()
        elif direction == flags.DOWN:
            if self._visual_cursor_pos[1] == self.height()-1:
                self.scrollDown()
            doc_cursor.toLineNext()
        elif direction == flags.LEFT:
            doc_cursor.toCharPrev()
        elif direction == flags.RIGHT:
            doc_cursor.toCharNext()
#                     flags.HOME: doc_cursor.toLineBeginning,
#                     flags.END: doc_cursor.toLineEnd,
