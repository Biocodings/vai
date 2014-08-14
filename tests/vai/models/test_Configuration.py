import unittest
from tests import fixtures
from vai.models import Configuration

class TestConfiguration(unittest.TestCase):
    def tearDown(self):
        Configuration._instance = None

    def testDefaultInit(self):
        config = Configuration.instance()
        self.assertEqual(config['colors.status_bar.fg'], 'cyan')

    def testInitFromFile(self):

        filename = fixtures.get("example_configuration.rc")

        config = Configuration.initFromFile(filename)

        self.assertEqual(config['colors.status_bar.fg'], 'red')





if __name__ == '__main__':
    unittest.main()
