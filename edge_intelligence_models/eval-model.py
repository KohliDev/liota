import tensorflow as tf
import tempfile
import pandas
import os

#tf.logging.set_verbosity(tf.logging.INFO)

BASE_DIRECTORY = '/Users/narun/PycharmProjects/ModelBuild/'
MODEL_BASE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'saved-windmill-model')
TEMP_MODEL_PATH = tempfile.mkdtemp(dir=MODEL_BASE_DIRECTORY)
TRAINING_FILE = os.path.join(BASE_DIRECTORY, 'windmill-data.csv')

COLUMNS = ["Timestamp", "windmill.RPM", "windmill.Vibration", "windmill.AmbientTemperature",
           "windmill.RelativeHumidity", "windmill.TurnOff"]
FEATURES = ["windmill.RPM", "windmill.Vibration"]
LABEL = "windmill.TurnOff"

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

    model_dir = tempfile.mkdtemp()
    print('Storing model file at ' + model_dir)
    e = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, model_dir=model_dir )

    e.fit(input_fn=input_fn_train, steps=20)
    return e

import tensorflow as tf

def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a graph_def into the
    # current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def,
            input_map=None,
            return_elements=None,
            name="prefix",
            op_dict=None,
            producer_op_list=None
        )
    return graph

def evaluate_model(model):

    # Evaluate for one step (one pass through the test data).
    results = model.evaluate(input_fn=input_fn_train, steps=1)

    # Print the stats for the evaluation.
    for key in sorted(results):
        print("%s: %s" % (key, results[key]))

    return results


g = load_graph(os.path.join(MODEL_BASE_DIRECTORY, "frozen_model.pb"))

# We can verify that we can access the list of operations in the graph
print("Printing Operations in the graph...")
for op in g.get_operations():
    print(op.name)

output = g.get_tensor_by_name('prefix/linear/binary_logistic_head/predictions/logistic:0')

'''
with tf.Session(graph=g) as sess:
    y_out = sess.run(output, feed_dict={
        x: []  
    })
    print(y_out)  # [[ False ]] Yay, it works!
'''
print(str(output))
