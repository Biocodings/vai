from .BufferCommand import BufferCommand
from .CommandResult import CommandResult
import copy

class DeleteLineAtCursorCommand(BufferCommand):
    def execute(self):
        document = self._document
        if document.isEmpty():
            return CommandResult(success=False, info=None)

        cursor = self._cursor
        self.saveCursorPos()

        if cursor.pos[0] == document.numLines():
            # Last line. Move the cursor up
            if not cursor.toLinePrev():
                # It's also the first line. Go at the beginning
                cursor.toLineBeginning()

        pos = cursor.pos
        self.saveLineMemento(pos[0], BufferCommand.MEMENTO_INSERT)

        old_line = copy.deepcopy(self.lastSavedMemento()[2])

        document.deleteLine(pos[0])

        # Deleted line, now we check the length of what comes up from below.
        # and set the cursor at the end of the line, if needed
        if document.lineLength(pos[0]) < pos[1]:
            cursor.toPos( (pos[0], document.lineLength(pos[0])))

        return CommandResult(success=True, info=old_line)


