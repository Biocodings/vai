import unittest
from vixtk import test, gui, core
from vix.widgets import SideRuler

class SideRulerTest(unittest.TestCase):
    def setUp(self):
        self.screen = test.VTextScreen((100,40))
        self.app = gui.VApplication([], screen=self.screen)

    def tearDown(self):
        del self.screen
        self.app.exit()
        core.VCoreApplication.vApp=None
        del self.app

    def testBasicSideRulerRepresentation(self):
        ruler = SideRuler(parent=None)
        ruler.setNumRows(10)
        ruler.setGeometry((0,0,5,40))
        ruler.show()
        self.app.processEvents()
        self.assertEqual(self.screen.stringAt(0,0,10),  " 1   .....")
        self.assertEqual(self.screen.stringAt(0,1,10),  " 2   .....")
        self.assertEqual(self.screen.stringAt(0,9,10),  "10   .....")
        self.assertEqual(self.screen.stringAt(0,10,10), "~    .....")

        ruler.setNumRows(100)
        self.app.processEvents()
        self.assertEqual(self.screen.stringAt(0,0,10),  "  1  .....")
        self.assertEqual(self.screen.stringAt(0,1,10),  "  2  .....")
        self.assertEqual(self.screen.stringAt(0,9,10),  " 10  .....")
        self.assertEqual(self.screen.stringAt(0,10,10), " 11  .....")


if __name__ == '__main__':
    unittest.main()
