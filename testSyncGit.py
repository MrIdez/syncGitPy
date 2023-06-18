import unittest

from syncGit import trouver_depot


class TestSyncGit(unittest.TestCase):
    def test_trouver_depot(self):
        self.assertEqual(trouver_depot("/home/guillaume/Cours"),
                         ['MathPython', 'Systeme', 'R203_Qualite_dev', 'BDD', 'Algo', 'Web'])  # add assertion here


if __name__ == '__main__':
    unittest.main()
