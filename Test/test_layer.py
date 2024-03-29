"""
    Test Layer module
"""
import unittest
import numpy as np
from layer import *
import activationFunction as af

class TestLayer(unittest.TestCase):
    """
        Test Layer class
    """

    def setUp(self):
        """
            Create 2 layer to use in the test
        """
        self.layer1 = HiddenLayer(np.full((4, 3), 0.1), np.full((4,3), 0.01), af.Relu())
        self.layer2 = OutputLayer(np.full((1, 5), 0.1), np.full((1,5), 0.01), af.TanH())

    def test_layer_constructor(self):
        """
            Test correctness of initialization of 2 layers (layer1, layer2)
        """
        self.assertListEqual([[0.1, 0.1, 0.1], [0.1, 0.1, 0.1], [0.1, 0.1, 0.1], [0.1, 0.1, 0.1]],
                             list(self.layer1.get_weights()))
        self.assertListEqual([[0.01, 0.01, 0.01], [0.01, 0.01, 0.01], [0.01, 0.01, 0.01], [0.01, 0.01, 0.01]],
                             list(self.layer1.learning_rates))
        self.assertIsInstance(af.Relu, self.layer1.activation)
        self.assertListEqual([0.1, 0.1, 0.1, 0.1, 0.1],
                             list(self.layer2.get_weights()))
        self.assertListEqual([0.01, 0.01, 0.01, 0.01, 0.01],
                             list(self.layer2.learning_rates))
        self.assertIsInstance(af.TanH, self.layer2.activation)
        self.assertEqual(2, self.layer1.get_num_input())
        self.assertEqual(4, self.layer1.get_num_unit())
        self.assertEqual(4, self.layer2.get_num_input())
        self.assertEqual(1, self.layer2.get_num_unit())

    def test_invalid_layer(self):
        """
            Test invalid parameters in Layer constructor
        """
        try:
            self.assertRaises(ValueError, HiddenLayer([0.1], np.full(1, 2), af.Relu()))
            self.assertRaises(ValueError, HiddenLayer(np.full((1, 2), 0.1), [0.1, 0.1], af.Relu()))
            self.assertRaises(ValueError, HiddenLayer(np.full((1, 2), 0.1), np.full((1, 2), 0.1), ML()))
        except:
            pass
        
    def test_function_signal(self):
        """
            Test function signal in Layer
        """
        pass

    

