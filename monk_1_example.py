"""
    Test our NN model using Monk3 dataset
"""
import numpy as np
from utility import read_monk_data
from neural_network import NeuralNetwork
from layer import OutputLayer, HiddenLayer
import weight_initializer as wi
import activation_function as af

def monk_example():
    """
        Test NN model using monk3 dataset
    """
    nn = NeuralNetwork(500, 'euclidean_loss', 'classification_accuracy', 0.8, nn_type="batch", batch_size=1)

    #create three layers

    train_data, train_label, _, _ = read_monk_data("dataset/monks-1.train", 1)
    test_data, test_label, _, _ = read_monk_data("dataset/monks-1.test")

    layer1 = HiddenLayer(weights=wi.he_initializer(15, len(train_data[0])),
                         learning_rates=np.full((15, len(train_data[0]) + 1),  0.8),
                         activation=af.Relu())
    layer2 = OutputLayer(weights=wi.he_initializer(1, 15),
                         learning_rates=np.full((1, 16), 0.8),
                         activation=af.Sigmoid())

    nn.add_layer(layer1)
    nn.add_layer(layer2)

    training_examples = list(zip(train_data, train_label))
    test_examples = list(zip(test_data, test_label))

    report = nn.fit(training_examples, test_examples)
    report.plot_loss()
    report.plot_accuracy()

if __name__ == "__main__":
    monk_example()