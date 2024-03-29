"""
Neural Network module implement a feedforward Neural Network
"""
import math
import numpy as np
import tqdm
from layer import Layer
from neural_exception import InvalidNeuralNetwork
from report import Report
from loss import loss_functions
from metric import metric_functions
from optimizer import optimizer_implemented


class NeuralNetwork:
    """
        Neural Network class to represent a feedforward Neural Network
    """

    def __init__(self, max_epochs, optimizer = 'SGD',loss='euclidean_loss', metric='',
                 momentum_rate=0, regularization_rate=0, batch_size=1):
        """create an instance of neural network class

        Args:
            max_epochs (int): number of maximum epochs used in param fitting.
            optimizer(string): indicate the Optimizer object used to train the model
            loss (string): Indicate the loss function to use to evaluate the model
            metric(string): indicate the metric used to evaluate the model, like Accuracy
            momentum_rate (int, optional): momentum_rate used for learning. Defaults to 0.
            regularization_rate(int,optional): regularization_rate used for learning. Defaults to 0
            batch_size (int, optional): size of batch used, Default set to 1.
            type_classifier (string, optional): estabilish the type of classification used
                            Accepted values are "Classification" and "Regression"
        """
        self.max_epochs = self.check_max_epochs(max_epochs)
        self.input_dimension = 0
        self.output_dimension = 0
        self.optimizer = self.check_optimizer(optimizer)
        self.batch_size = self.check_batch_size(batch_size)

        # note: this is not a np.ndarray object
        self.layers = []
        self.momentum_rate = self.check_momentum(momentum_rate)
        self.regularization_rate = self.check_regularization(
            regularization_rate)
        self.metric = self.check_metric(metric)
        self.loss = self.check_loss(loss)

        self.topology = []

    def init_params(self, parameters):
        """
            NN constructor which we pass a dict of parameters
            Param:
                parameters(dict): dictionary of parameters of NN object
        """
        max_epoch = parameters['num_epoch']
        momentum_rate = parameters['momentum']
        loss = parameters['loss_function']
        accuracy = parameters['accuracy']
        regularization = parameters['regularization']
        batch_size = parameters['batch_size']
        optimizer = parameters['optimizer'] if parameters['optimizer'] is not None else 'batch'
        self.__init__(max_epoch, optimizer, loss, accuracy, momentum_rate, regularization, batch_size)
        
    def deepcopy(self):
        """
            Implement the deep copy of Neural Network object
        """
        newNN = NeuralNetwork(self.max_epochs, self.loss, self.metric, self.momentum_rate,
                              self.regularization_rate, self.type, self.batch_size, self.type_classifier)
        [newNN.add_layer(layer.deepcopy()) for layer in self.layers]
        return newNN
        

    def check_batch_size(self, batch_size):
        """
            Check batch_size value inserted in NN constructor
            Param:
                batch_size(float): rate used as batch_size and should be > 0
            Return:
                batch_size is 1 if self.optimizer is SGD
                batch_size if self.optimizer is != SGD and batch_size > 0
                otherwise raise InvalidNeuralNetwork exception
        """
        if self.optimizer == "SGD" and batch_size == 1:
            return batch_size
        elif batch_size > 0:
            return batch_size
        else:
            raise InvalidNeuralNetwork()

    def check_loss(self, loss):
        """
            Check valid loss function inserted in NN constructor
            Param:
                loss(string): name of loss function to use to evaluate NN model
            Return:
                loss if is a valid loss function otherwise raise InvalidNeuralNetwork exception.
        """
        if loss in loss_functions:
            return loss
        else:
            raise InvalidNeuralNetwork()

    def check_max_epochs(self, max_epochs):
        """
            Check max_epochs value inserted in constructor
            Param:
                max_epochs(int): number of epochs used in NN training and need to be > 0
            Return:
                max_epochs if >0 otherwise raise InvalidNeuralNetwork exception
        """
        if max_epochs > 0:
            return max_epochs
        else:
            raise InvalidNeuralNetwork()

    def check_metric(self, metric):
        """
            Check metric value inserted in NN constructor
            Param:
                metric(string): name of metric function used to evaluate NN model
            Return:
                metric if is a valid metric function otherwise raise InvalidNeuralNetwork exception
        """

        if metric in metric_functions or metric == '':
            return metric
        else:
            raise InvalidNeuralNetwork()

    def check_momentum(self, momentum_rate):
        """
            Check momentum_rate value inserted in Constructor

            Param:
                momentum_rate(float): rate used as momentum and should be >= 0
            Return:
                momentum_rate if is >= 0 otherwise raise InvalidNeuralNetwork exception
        """
        if momentum_rate >= 0:
            return momentum_rate
        else:
            raise InvalidNeuralNetwork()

    def check_optimizer(self, optimizer):
        """
            Check optimizer value inserted in NN constructor
            Param:
                optimizer(string): name of optimizer object used to train NN model
            Return:
                optimizer if is a valid optimizer object otherwise raise InvalidNeuralNetwork exception
        """
        if optimizer in optimizer_implemented:
            return optimizer
        else:
            raise InvalidNeuralNetwork()

    def check_regularization(self, regularization_rate):
        """
            Check regularization_rate value inserted in NN costructor
            Param:
                regularization_rate(float): rate used as regularization and should be >= 0
            Return:
                regularization_rate if is >= 0 otherwise raise InvalidNeuralNetwork exception
        """
        if regularization_rate >= 0:
            return regularization_rate
        else:
            raise InvalidNeuralNetwork()

    def check_type_classifier(self, type_classifier):
        """
            Check type of Classifier for NN model
            Param:
                type_classifier(string): type of classifier and valid value
                                         are classification and regression
            Return:
                type_classifier if is a valid value otherwise raise InvalidNeuralNetwork exception
        """
        if type_classifier in ["classification", "regression"]:
            return type_classifier
        else:
            raise InvalidNeuralNetwork()

    def add_layer(self, layer):
        """ add a layer in the neural network

            Parameters:
                layer (Layer): layer to be added. The layer must have a number
                of input equal to the unit of the previous layer

            Raises:
                ValueError: the layer is not a Layer object
                ValueError: The number of input for this new layer is not equal
                  to the number of unit of the previous layer in the neural network

            Example:
                this is a neural network with two layers

                      o   o   o
                    o   o   o   o

                Then we execute neuralNetwork.addLayer(layer)
                where layer has 2 units with 3 inputs(o o):

                        o   o
                      o   o   o
                    o   o   o   o

        """

        if not isinstance(layer, Layer):
            raise ValueError('layer must be a Layer object')

        # the first layer added define the input dimension of the neural network
        if len(self.layers) == 0:
            self.input_dimension = layer.get_num_input()
            self.topology.append(layer.get_num_input())
        # the new layer must have an input dimension equal
        # to the number of units in the last layer added
        elif layer.get_num_input() != self.output_dimension:
            raise ValueError(
                "The number of input for this new layer must be equal to previous layer")

        self.topology.append(layer.get_num_unit())

        # the last layer inserted define the output dimension
        self.output_dimension = layer.get_num_unit()

        self.layers.append(layer)

    def predict(self, sample):
        """
            Predict method implement the predict operation to make prediction
            about predicted output of a sample

            Parameters:
                sample(nparray of input patterns): input/inputs for which returning the predictions

            Precondition:
                The length of sample is equal to input dimension in NN

            Return: the predicted target over the sample
        """
        # sample dimension controlled in _feedwardSignal
        return self._feedward_signal(sample)

    def _feedward_signal(self, sample):
        """
            FeedwardSignal feedward the signal from input to output of a feedforward NN

            Parameters:
                sample(nparray of input patterns): input/inputs for which returning the predictions

            Precondition:
                The length of sample is equal to input dimension in NN

            Return: the predicted output obtained after propagation of signal
        """
        if sample.shape[1] != self.input_dimension:
            raise ValueError

        input_layer = sample

        for layer in self.layers:
            output_layer = layer.function_signal(input_layer)
            input_layer = output_layer

        return output_layer

    def fit(self, training_examples, validation_samples=None, test_samples=None, min_error=1e-12):
        """training of the neural network using the training examples

        Parameters:
            training_examples (array(tupla(input, target))): Training samples.
            validation_samples (array(tupla(input, target))): Validation samples (default None)
            test_samples (array(tupla(input, target))): Test samples to use in test (default None)
            min_error (float): Training stops whenever loss error 
            becomes greater or equale than min_error . Defaults to 1e-12.
        
        Returns:
            (Report): Report of the training. 
            The object contains the training/*validation/*test error measured at the end of every epoch.
            * only if validation samples and test samples is not None.
        """

        # create empty Report object
        report = Report(self.max_epochs, min_error)
        total_samples = len(training_examples)

        if self.optimizer == "SGD":
            self.batch_size = total_samples

        # executed epochs
        num_epochs = 0
        #error calculated at the end of each epoch
        error = np.Inf
        #number of sets into which split the training set (e.g. for batch is 1)
        num_window = math.ceil(total_samples // self.batch_size)

        inputs_training = np.array([elem[0] for elem in training_examples])
        targets_training = np.array([elem[1] for elem in training_examples])

        if validation_samples:
            inputs_validation = np.array([elem[0]
                                          for elem in validation_samples])
            targets_validation = np.array([elem[1]
                                           for elem in validation_samples])

        # ratio between batch size and the total number of samples
        batch_total_samples_ratio = self.batch_size/total_samples

        for num_epochs in tqdm.tqdm(range(self.max_epochs), desc="fit"):

            # shuffle training examples
            np.random.shuffle(training_examples)

            #optimizer_implemented[self.optimizer].train(training_examples)
            # training
            for index in range(0, num_window):
                window_examples = training_examples[index * self.batch_size:
                                                    (index+1) * self.batch_size]

                # Backpropagate training examples
                optimizer_implemented[self.optimizer]()._back_propagation(
                    self, window_examples, batch_total_samples_ratio,
                    loss_functions[self.loss])

            #calculate training/*validation/*(test) error after one epoch

            training_predicted = self.predict(inputs_training)

            # calculate loss on training set
            error = loss_functions[self.loss].loss(
                training_predicted,
                targets_training,
            )

            #adding error in the report
            report.add_training_error(error, num_epochs)

            # calculate accuracy on training set
            if self.metric != '':
                accuracy = metric_functions[self.metric](
                    training_predicted,
                    targets_training)
                #adding accuracy in the report
                report.add_training_accuracy(accuracy, num_epochs)

            #Doing the same for validation set if validation_set is defined
            if validation_samples:
                val_predicted = self.predict(inputs_validation)
                validation_error = loss_functions[self.loss].loss(
                    val_predicted,
                    targets_validation,
                )
                if self.metric != '':
                    accuracy = metric_functions[self.metric](
                        val_predicted,
                        targets_validation)
                    report.add_validation_accuracy(accuracy, num_epochs)

                report.add_validation_error(
                    error, validation_error, num_epochs)

            #Doing the same for test set if test_set is defined
            if test_samples:
                test_error = loss_functions[self.loss].loss(
                    [self.predict(test_example[0])
                     for test_example in test_samples],
                    [test_example[1] for test_example in test_samples],
                ) / len(test_samples)
                report.add_test_error(test_error, num_epochs)

            # check error
            if error <= min_error:
                break

            # update the learning rate
            [layer.update_learning_rate(num_epochs) for layer in self.layers]

        return report
