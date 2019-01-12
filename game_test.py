import unittest

from game import validate_reading

class TestReadingValidation(unittest.TestCase):
    """
    Our basic test class
    """

    def test_validation_reading(self):
        """
        The actual test.
        Any method which starts with ``test_`` will considered as a test case.
        """
        res = validate_reading("abc")
        self.assertEqual(res, "abc")


if __name__ == '__main__':
    unittest.main()
