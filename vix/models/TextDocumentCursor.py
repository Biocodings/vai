from vixtk import core

class TextDocumentCursor(core.VObject):
    def __init__(self, text_document):
        self._text_document = text_document
        self._text_document.registerCursor(self)
        self._pos = (1,1)
        self._optimistic_column = 1

        self.positionChanged = core.VSignal(self)

    def currentLine(self):
        return self._text_document.getLine(self._pos[0])

    def pos(self):
        return self._pos

    def moveTo(self, pos):
        line, column = pos
        if line < 1 or line > self._text_document.numLines() or column < 1:
            return False

        self._pos = (line, min(self._text_document.lineLength(line), column))
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toLine(self, line):
        column = self.pos()[1]
        if line < 1 or line > self._text_document.numLines() or column < 1:
            return False

        self._pos = (line, min(self._text_document.lineLength(line), column))
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toLineNext(self):
        if self._pos[0] >= self._text_document.numLines():
            return False
        self._pos = (self._pos[0]+1,
                                    min(
                                        self._text_document.lineLength(self._pos[0]+1),
                                        max(self._pos[1],
                                            self._optimistic_column
                                           )
                                        )
                    )
        self.positionChanged.emit(self._pos)
        return True

    def toLinePrev(self):
        if self._pos[0] == 1:
            return False

        self._pos = (self._pos[0]-1,
                                    min(
                                        self._text_document.lineLength(self._pos[0]-1),
                                        max(self._pos[1],
                                            self._optimistic_column
                                           )
                                        )
                    )
        self.positionChanged.emit(self._pos)
        return True

    def toCharNext(self):
        if self._pos[1] == self._text_document.lineLength(self._pos[0]):
            return False

        self._pos = (self._pos[0], self._pos[1]+1)
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toCharPrev(self):
        if self._pos[1] == 1:
            return False

        self._pos = (self._pos[0], self._pos[1]-1)
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toLineBeginning(self):
        self._pos = (self._pos[0], 1)
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toLineEnd(self):
        self._pos = (self._pos[0], self._text_document.lineLength(self._pos[0]))
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toFirstLine(self):
        self._pos = (1,1)
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def toLastLine(self):
        self._pos = (self._text_document.numLines(), 1)
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)
        return True

    def lineLength(self):
        return self._text_document.lineLength(self._pos[0])

    def updateLineMeta(self, meta_dict):
        self._text_document.updateLineMeta(self._pos[0], meta_dict)

    def lineMeta(self):
        return self._text_document.lineMeta(self._pos[0])

    def updateCharMeta(self, line_number, meta_dict): pass
    def charMeta(self): pass

    def newLineAfter(self):
        self._text_document.createLineAfter(self._pos[0])

    def newLine(self):
        self._text_document.createLine(self._pos[0])

    def deleteLine(self):
        current_line = self._pos[0]
        if current_line == self._text_document.numLines():
            self.toLinePrev()
        self._text_document.deleteLine(current_line)

    def insertChar(self, char):
        self._text_document.insert(self._pos, char)
        self.toCharNext()

    def deleteChar(self):
        if self.toCharPrev():
            self._text_document.delete(self._pos, 1)

    def deleteCharAfter(self):
        current_column = self._pos[1]
        if current_column == self._text_document.lineLength(self._pos[0]):
            if self.toCharPrev():
                self._text_document.delete( (self._pos[0], current_column), 1)
        else:
            self._text_document.delete( (self._pos[0], current_column), 1)

    def replace(self, length, replace): pass

    def breakLine(self):
        self._text_document.breakLine(self._pos)
        self._pos = (self._pos[0]+1, 1)
        self._optimistic_column = self._pos[1]
        self.positionChanged.emit(self._pos)

    def joinWithNextLine(self):
        self._text_document.joinWithNextLine(self._pos[0])

