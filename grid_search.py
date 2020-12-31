"""
    Module grid_search to do the grid search for ML models
"""
from layer import HiddenLayer, OutputLayer
from utility import normalize_data, read_cup_data, denormalize_data
import cross_validation as cv
import multiprocessing
import csv
import itertools
import time
import learning_rate as lr
import weight_initializer as wi
import activation_function as af
from neural_network import NeuralNetwork
from bagging import Bagging
from loss import loss_functions
from metric import metric_functions

# Parameters which we conduct our GridSearch on our NN model
parameters = {
    'learning_rates': [0.08, 0.1, 0.13],
    'regularization': [0, 0.0005, 0.0008, 0.001, 0.0015],
    'momentum': [0.6, 0.8, 1.0],
    'weight_initialization': [wi.xavier_initializer, wi.ranged_uniform_initializer],
    'activation_hidden': [af.TanH, af.Relu],
    'type_nn': ['batch'],
    'batch_size': [1],
    'topology': [(10,), (5, 5), (20,), (10, 5, 5), (5, 10)],
    'loss': ['mean_squared_error'],
    'accuracy': ['euclidean_loss'],
    'num_epoch': [500],
}

train_data, train_label, test_data, test_label = read_cup_data(
    "dataset/ML-CUP20-TR.csv", 0.8)
train_data, train_label, _, _ = normalize_data(train_data, train_label)
dataset = list(zip(train_data, train_label))


def run(model, results, model_param, dataset):
    """
        Proxy function where it will start cross validation on a configuration
        in an asyncro way

        Param:
            model(NeuralNetwork): NeuralNetwork object to use
            results(List): List of results obtained in GridSearch
            model_param(dict): dict of param of model object
            Return nothing but add result from cross validation and model_param in results list
    """
    average_vl, sd_vl, average_tr_error_best_vl, reports = cv.cross_validation(
        model, dataset, 4)
    results.append({
        'accuracy_average_vl': average_vl,
        'accuracy_sd_vl': sd_vl,
        'average_tr_error_best_vl': average_tr_error_best_vl,
        'model_param': model_param,
    })
    print("Finish {} cross-validation".format(len(results)))


def initialize_model(model_param, num_features, output_dim):
    """
        Create NN model to use to execute a cross validation on it

        Param:
            model_param(dict): dictionary of param to use to create NN object

        Return a NN model with also complete graph topology of the network
    """
    print(model_param)
    learning_rate = model_param[0]
    regularization = model_param[1]
    momentum = model_param[2]
    weight_initialization = model_param[3]
    activation = model_param[4]
    type_nn = model_param[5]
    batch_size = model_param[6]
    topology = model_param[7]
    loss = model_param[8]
    accuracy = model_param[9]
    num_epochs = model_param[10]

    # Create NN object model
    model = NeuralNetwork(num_epochs, loss, accuracy, momentum,
                          regularization, type_nn, batch_size)

    last_dim = num_features
    # Add Layers
    print(topology)
    for num_nodes in topology:
        layer = HiddenLayer(weight_initialization(num_nodes, last_dim),
                            lr.Constant(num_nodes, last_dim, learning_rate),
                            activation())
        model.add_layer(layer)
        last_dim = num_nodes
    output_layer = OutputLayer(weight_initialization(output_dim, last_dim),
                               lr.Constant(output_dim, last_dim,
                                           learning_rate),
                               af.Linear())
    model.add_layer(output_layer)
    print('momentum:', model.momentum_rate)
    return model


if __name__ == '__main__':

    def grid_search(params, dataset, num_features, output_dim, n_threads=5, save_path='grid_results/grid.csv'):
        """
            Execute Grid Search

            Param:
                save_path(str): string of file path

        """
        params = [
            params['learning_rates'],
            params['regularization'],
            params['momentum'],
            params['weight_initialization'],
            params['activation_hidden'],
            params['type_nn'],
            params['batch_size'],
            params['topology'],
            params['loss'],
            params['accuracy'],
            params['num_epoch']
        ]
        pool = multiprocessing.Pool(multiprocessing.cpu_count()) if n_threads is None else \
            multiprocessing.Pool(n_threads)
        results = multiprocessing.Manager().list()

        start = time.time()
        for model_param in list(itertools.product(*params)):
            model = initialize_model(model_param, num_features, output_dim)
            print("Model:", model)
            pool.apply_async(func=run,
                             args=(model, results, model_param, dataset))

        pool.close()
        pool.join()

        # Sort results according to the accuracy of models

        # l_results = list(results.sort(key=lambda x: x['accuracy_average_vl'], reverse=True))

        # Write to file results obtained
        write_results(results, save_path)

        with open('grid_results/grid_info.txt', 'a') as info_file:
            total_time = time.gmtime(time.time() - start)
            info_file.write("Grid Search ended in {} hour {} minutes {} seconds \n".format(
                total_time.tm_hour, total_time.tm_min, total_time.tm_sec))
        return results[0]

    def write_results(results, file_path):
        """
            Write results obtained by GridSearch in a txt file
            Param:
                file_path(str): path where we will save our results on GridSearch
        """
        with open(file_path, 'w') as result_file:
            writer = csv.writer(result_file)
            writer.writerow(['accuracy_average_vl', 'accuracy_sd_vl', 'average_tr_error_best_vl',
                             'learning_rate', 'regularization', 'momentum', 'activation_hidden',
                             'weight_init', 'topology'])

            for item in results:
                writer.writerow([
                    str(item['accuracy_average_vl']),
                    str(item['accuracy_sd_vl']),
                    str(item['average_tr_error_best_vl']),
                    str(item['model_param'][0]),
                    str(item['model_param'][1]),
                    str(item['model_param'][2]),
                    str(item['model_param'][4]),
                    str(item['model_param'][3]),
                    item['model_param'][7]
                ])
        return None

    #grid_search(parameters, dataset, len(train_data[0]), len(train_label[0]),)


# BAGGING FINAL RESULTS

def final_model():
    
    model_params = [
        [0.1, 0, 0.6, wi.ranged_uniform_initializer, af.TanH, 'batch',
            1, (10, 5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.1, 0.0005, 1.0, wi.xavier_initializer, af.TanH, 'batch',
            1, (10, 5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0008, 0.6, wi.ranged_uniform_initializer, af.TanH, 'batch',
            1, (10, 5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0005, 1.0, wi.xavier_initializer, af.TanH, 'batch',
            1, (5, 10), 'mean_squared_error', 'euclidean_loss', 500],
        [0.1, 0.0008, 0.8, wi.ranged_uniform_initializer, af.TanH, 'batch',
            1, (10, 5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0005, 0.8, wi.xavier_initializer, af.TanH, 'batch',
            1, (5,5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0005, 0.6, wi.xavier_initializer, af.TanH, 'batch',
            1, (10, 5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0005, 0.8, wi.ranged_uniform_initializer, af.TanH, 'batch',
            1, (10, 5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0005, 1.0, wi.xavier_initializer, af.TanH, 'batch',
            1, (5, 5), 'mean_squared_error', 'euclidean_loss', 500],
        [0.13, 0.0005, 0.8, wi.xavier_initializer, af.TanH, 'batch',
            1, (5,10), 'mean_squared_error', 'euclidean_loss', 500],
    ]

    train_data, train_label, test_data, test_label = read_cup_data("dataset/ML-CUP20-TR.csv", 0.8)
    train_data, train_label, den_data, den_label = normalize_data(train_data, train_label)
    test_data, test_label,_,_ =  normalize_data(test_data, test_label, den_data, den_label)

    training_examples = list(zip(train_data, train_label))
    test_examples = list(zip(test_data, test_label))


    ensemble = Bagging(len(training_examples))

    #create and add the model to the ensemble

    for model_param in model_params:
        nn = initialize_model(model_param, len(train_data[0]), 2)
        ensemble.add_neural_network(nn)
    
    #training all the models in the ensemble

    ensemble.fit(training_examples, test_examples)
    
    #check models performance

    i = 1
    for model in ensemble.models:
        predicted_training_data = denormalize_data(model.predict(train_data), den_label)
        error = metric_functions['euclidean_loss'](
                predicted_training_data,
                denormalize_data(train_label, den_label)
            )
        print("model ", i, ", training: ", error)
        
        predicted_test_data = denormalize_data(model.predict(test_data), den_label)
        error = metric_functions['euclidean_loss'](
                predicted_test_data,
                denormalize_data(test_label, den_label)
            )
        
        print("model ", i, ", test: ", error)
        i += 1
    
    #check ensemble performance

    predicted_training_data = denormalize_data(ensemble.predict(train_data), den_label)
    error = metric_functions['euclidean_loss'](
                predicted_training_data,
                denormalize_data(train_label, den_label)
        )
    print("ensemble training: ", error)
        
    predicted_test_data = denormalize_data(ensemble.predict(test_data), den_label)
    error = metric_functions['euclidean_loss'](
            predicted_test_data,
            denormalize_data(test_label, den_label)
    )
        
    print("ensemble test: ", error)

    #print("error ensembled:", report.get_vl_accuracy())
    
    return ensemble

#final_model()



"""
17.3424323806
9.549290397010338
6.857825099432584
3.9735023822009112
9.848623616101907
4.146277949131173
7.970618203289681
8.80459194896491
8.001441124426606
4.521621670599758

7.929469230439691

model_param = [
    0.13,
    0.0008,
    0.8,
    wi.ranged_uniform_initializer,
    af.TanH,
    'batch',
    1,
    (10,5,5),
    'mean_squared_error',
    'euclidean_loss',
    500
]

train_data, train_label, _, _ = read_cup_data("dataset/ML-CUP20-TR.csv", 0.8)
# train_data, train_label, _, _ = read_monk_data("dataset/monks-1.train", 1)
train_data, train_label = normalize_data(train_data, train_label)

nn = initialize_model(model_param, len(train_data[0]), 2)
training_examples = list(zip(train_data, train_label))


report = nn.fit(training_examples)
report.plot_accuracy()
print("training mse", report.training_error[-1])
print("validation mse", report.get_vl_error())
print("training accuracy", report.training_accuracy[-1])
print("validation accuracy", report.get_vl_accuracy())
"""
