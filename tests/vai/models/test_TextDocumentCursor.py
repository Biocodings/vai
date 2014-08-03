import os
import sys
import inspect
import unittest
from vixtk.test import VSignalSpy
from vix.models.TextDocument import TextDocument
from vix.models.TextDocumentCursor import TextDocumentCursor
from vix import flags
from tests import fixtures

class TestTextDocumentCursor(unittest.TestCase):

    def setUp(self):
        self.doc = TextDocument(fixtures.get("basic_nonempty_file.txt"))

    def testPos(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertEqual(cursor.pos(), (1,1))
        cursor.toPos( (1,4) )
        self.assertEqual(cursor.pos(), (1,4))

    def testTextDocument(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertEqual(cursor.textDocument(), self.doc)

    def testLineText(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertEqual(cursor.lineText(), 'hello\n')
        cursor.toPos( (1,4) )
        self.assertEqual(cursor.lineText(), 'hello\n')

    def testToPos(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertTrue(cursor.toPos( (1,1) ))
        self.assertTrue(cursor.toPos( (1,3) ))
        self.assertFalse(cursor.toPos( (0,1) ))
        self.assertFalse(cursor.toPos( (1,0) ))
        self.assertFalse(cursor.toPos( (1,30) ))
        self.assertFalse(cursor.toPos( (30,1) ))

    def testToLine(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertTrue(cursor.toLine(1))
        self.assertTrue(cursor.toLine(2))
        self.assertFalse(cursor.toLine(-1))
        self.assertFalse(cursor.toLine(30))

    def testToLinePrev(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertFalse(cursor.toLinePrev())
        self.assertTrue(cursor.toLine(2))
        self.assertTrue(cursor.toLinePrev())

    def testToLineNext(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertTrue(cursor.toLineNext())
        self.assertFalse(cursor.toLineNext())

    def testToCharPrev(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertFalse(cursor.toCharPrev())
        cursor.toPos((1,4))
        self.assertTrue(cursor.toCharPrev())
        self.assertTrue(cursor.toCharPrev())
        self.assertTrue(cursor.toCharPrev())
        self.assertFalse(cursor.toCharPrev())

    def testToCharNext(self):
        cursor = TextDocumentCursor(self.doc)
        self.assertTrue(cursor.toCharNext())
        self.assertTrue(cursor.toCharNext())
        self.assertTrue(cursor.toCharNext())
        self.assertTrue(cursor.toCharNext())
        self.assertTrue(cursor.toCharNext())
        self.assertFalse(cursor.toCharNext())

    def testToLineBeginning(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.toLineBeginning()
        self.assertEqual(cursor.pos(), (1,1))

    def testToLineEnd(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.toLineEnd()
        self.assertEqual(cursor.pos(), (1,6))

    def testToFirstLine(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((2,4))
        cursor.toFirstLine()
        self.assertEqual(cursor.pos(), (1,1))

    def testToLastLine(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.toLastLine()
        self.assertEqual(cursor.pos(), (2,1))

    def testLineLength(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        self.assertEqual(cursor.lineLength(), 6)

    def testNewLineAfter(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.newLineAfter()

    def testNewLine(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.newLine()

    def testDeleteLine(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.deleteLine()

    def testBreakLine(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.breakLine()

    def testJoinWithNextLine(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.joinWithNextLine()

    def testInsertSingleChar(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.insertSingleChar('h')

    def testDeleteSingleCharAfter(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.deleteSingleCharAfter()

    def testDeleteSingleChar(self):
        cursor = TextDocumentCursor(self.doc)
        cursor.toPos((1,4))
        cursor.deleteSingleChar()

    """
    def updateLineMeta(self, meta_dict):
    def lineMeta(self):
    def updateCharMeta(self, line_number, meta_dict): pass
    def charMeta(self): pass
    def replace(self, length, replace):
    """

if __name__ == '__main__':
    unittest.main()
