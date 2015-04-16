import unittest
from vai import models
from vai.models import commands
from tests import fixtures


class TestNewLineAfterCommand(unittest.TestCase):
    def setUp(self):
        self.buffer = models.Buffer()
        with open(fixtures.get("basic_python.py"), 'r') as f:
            self.buffer.document.read(f)

    def testNewLineAfterCommand(self):
        doc = self.buffer.document
        cursor = self.buffer.cursor

        command = commands.NewLineAfterCommand(self.buffer)
        status = command.execute()

        self.assertNotEqual(status, None)
        self.assertTrue(status.success)
        self.assertEqual(doc.numLines(), 5)
        self.assertEqual(doc.lineMetaInfo("Change").data(1), None)
        self.assertEqual(doc.lineMetaInfo("Change").data(2), "added")
        self.assertEqual(doc.lineMetaInfo("Change").data(3), None)
        self.assertNotEqual(doc.lineText(1), "\n")
        self.assertEqual(doc.lineText(2), "\n")
        self.assertEqual(cursor.pos, (2,1))

        command.undo()
        self.assertEqual(doc.numLines(), 4)
        self.assertEqual(doc.lineMetaInfo("Change").data(1), None)
        self.assertEqual(doc.lineMetaInfo("Change").data(2), None)
        self.assertEqual(cursor.pos, (1,1))

        self.buffer.cursor.toPos((4,7))
        command = commands.NewLineAfterCommand(self.buffer)
        status = command.execute()
        self.assertNotEqual(status, None)
        self.assertEqual(doc.numLines(), 5)
        self.assertEqual(cursor.pos, (5,5))
        self.buffer.cursor.toLinePrev()
        self.assertEqual(cursor.pos, (4,5))
        command.undo()

    def testRedo(self):
        doc = self.buffer.document
        cursor = self.buffer.cursor
        cursor.toPos((1,1))

        command = commands.NewLineAfterCommand(self.buffer)

        command.execute()
        command.undo()
        cursor.toPos((4,1))
        command.execute()

        self.assertEqual(doc.numLines(), 5)
        self.assertNotEqual(doc.lineText(1), "\n")
        self.assertEqual(doc.lineText(2), "\n")
        self.assertEqual(cursor.pos, (2,1))

if __name__ == '__main__':
    unittest.main()
