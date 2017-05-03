import tensorflow as tf
import tempfile
import pandas
import os
from tensorflow.python.framework import graph_util

#tf.logging.set_verbosity(tf.logging.INFO)

BASE_DIRECTORY = '/Users/narun/PycharmProjects/ModelBuild/'
MODEL_BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'saved-windmill-model')
TEMP_MODEL_PATH = tempfile.mkdtemp(dir=MODEL_BASE_DIRECTORY)
TRAINING_FILE = os.path.join(BASE_DIRECTORY, 'windmill-data.csv')

COLUMNS = ["Timestamp", "windmill.RPM", "windmill.Vibration", "windmill.AmbientTemperature",
           "windmill.RelativeHumidity", "windmill.TurnOff"]
FEATURES = ["windmill.RPM", "windmill.Vibration"]
LABEL = "windmill.TurnOff"

#df[TURNOFF_COLUMN] = (df["windmill.RPM"].apply(lambda x: ">10" in x)).astype(int)
#df[TURNOFF_COLUMN] = (df["windmill.Vibration"].apply(lambda x: ">0.5" in x)).astype(float)
#df[TURNOFF_COLUMN] = (df["windmill.TurnOff"].apply(lambda x: ">0" in x)).astype(int)


def input_fn(data_set):
    features = {k: tf.constant(data_set[k].values)
                       for k in FEATURES}
    label = tf.constant(data_set[LABEL].values)

    return features, label

def input_fn_train():
    training_set = pandas.read_csv(TRAINING_FILE, names=COLUMNS, skipinitialspace=True, skiprows=1)
    return input_fn(training_set)

def build_model():
    feature_cols = [tf.contrib.layers.real_valued_column(k)
                    for k in FEATURES]

    optimizer = tf.train.FtrlOptimizer(
        learning_rate=0.1,
        l1_regularization_strength=1.0,
        l2_regularization_strength=1.0)

    print('Storing model checkpoints at ' + TEMP_MODEL_PATH)

    e = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, optimizer=optimizer, model_dir=TEMP_MODEL_PATH )

    e.fit(input_fn=input_fn_train, steps=20)
    return e

def evaluate_model(model):

    # Evaluate for one step (one pass through the test data).
    results = model.evaluate(input_fn=input_fn_train, steps=1)

    # Print the stats for the evaluation.
    for key in sorted(results):
        print("%s: %s" % (key, results[key]))

    return results


def freeze_graph(model_folder, save_folder):
    # We retrieve our checkpoint fullpath
    checkpoint = tf.train.get_checkpoint_state(model_folder)
    input_checkpoint = checkpoint.model_checkpoint_path

    # We precise the file fullname of our freezed graph
    #absolute_model_folder = "/".join(input_checkpoint.split('/')[:-1])
    output_graph_filepath = os.path.join(save_folder, "frozen_model.pb")

    # Before exporting our graph, we need to precise what is our output node
    # This is how TF decides what part of the Graph he has to keep and what part it can dump
    # NOTE: this variable is plural, because you can have multiple output nodes
    output_node_names = [
        "linear/binary_logistic_head/predictions/zeros_like",
        "linear/binary_logistic_head/predictions/concat/axis",
        "linear/binary_logistic_head/predictions/concat",
        "linear/binary_logistic_head/predictions/logistic",
        "linear/binary_logistic_head/predictions/probabilities",
        "linear/binary_logistic_head/predictions/classes/dimension",
        "linear/binary_logistic_head/predictions/classes"]

    # We clear devices to allow TensorFlow to control on which device it will load operations
    clear_devices = True

    # We import the meta graph and retrieve a Saver
    saver = tf.train.import_meta_graph(input_checkpoint + '.meta', clear_devices=clear_devices)

    # We retrieve the protobuf graph definition
    graph = tf.get_default_graph()
    input_graph_def = graph.as_graph_def()

    # We start a session and restore the graph weights
    with tf.Session() as sess:
        saver.restore(sess, input_checkpoint)

        #print(input_graph_def)

        # We use a built-in TF helper to export variables to constants
        output_graph_def = graph_util.convert_variables_to_constants(
            sess,  # The session is used to retrieve the weights
            input_graph_def,  # The graph_def is used to retrieve the nodes
            output_node_names  # The output node names are used to select the useful nodes
        )

        # Finally we serialize and dump the output graph to the filesystem
        with tf.gfile.GFile(output_graph_filepath, "wb") as f:
            f.write(output_graph_def.SerializeToString())
        print("%d ops in the final graph." % len(output_graph_def.node))


with tf.Graph().as_default() as g:
    with tf.Session() as sess:
        # Initializes all the variables.
        init_all_op = tf.global_variables_initializer()
        sess.run(init_all_op)

        mymodel = build_model()
        #print(mymodel)
        #evaluate_model(mymodel)

        print("Printing the model...")
        print(mymodel)

        print("Listing variables in the model...")
        for var in mymodel.get_variable_names():
            print(str(var) + '::' + str(mymodel.get_variable_value(var)))

        #print("Listing operations in global Graph...")
        #for op in g.get_operations():
        #    print(op.name)

        freeze_graph(TEMP_MODEL_PATH, MODEL_BASE_DIRECTORY)

        #model_var = tf.Variable(mymodel, name='windmill_model')

        #print('Printing variables...')
        #print([v.op.name for v in tf.global_variables()])

        # Creates a saver.
        #saver0 = tf.train.Saver(['windmill_model'])
        #saver0 = tf.train.Saver()
        #saver0.save(sess, SAVED_MODEL_PATH)

        # Generates MetaGraphDef.
        #saver0.export_meta_graph(SAVED_MODEL_PATH + '.meta')
