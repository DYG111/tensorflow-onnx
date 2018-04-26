# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.

"""
python -m tf2onnx.convert : tool to convert a frozen tensorflow to onnx
"""
import argparse
import sys

import onnx
import tensorflow as tf
from tf2onnx.tfonnx import process_tf_graph, tf_optimize, DEFAULT_TARGET, POSSIBLE_TARGETS

#just test
def get_args():
    """Parse commandline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="input model file")
    parser.add_argument("--output", help="output model file")
    parser.add_argument("--inputs", required=True, help="model input_names")
    parser.add_argument("--outputs", required=True, help="model output_names")
    parser.add_argument("--target", default=",".join(DEFAULT_TARGET), help="target platform")
    parser.add_argument("--continue_on_error", help="continue_on_error", action="store_true")
    parser.add_argument("--verbose", help="verbose output", action="store_true")
    args = parser.parse_args()

    if args.inputs:
        args.inputs = args.inputs.split(",")
    if args.outputs:
        args.outputs = args.outputs.split(",")
    if args.target:
        args.target = args.target.split(",")
        for target in args.target:
            if target not in POSSIBLE_TARGETS:
                print("unknown target ", target)
                sys.exit(1)

    return args


def main():
    args = get_args()

    print("using tensorflow={}, onnx={}".format(tf.__version__, onnx.__version__))

    graph_def = tf.GraphDef()
    with tf.gfile.FastGFile(args.input, 'rb') as f:
        graph_def.ParseFromString(f.read())
    graph_def = tf_optimize(None, args.inputs, args.outputs, graph_def)
    with tf.Graph().as_default() as tf_graph:
        tf.import_graph_def(graph_def, name='')
    with tf.Session(graph=tf_graph) as sess:
        g = process_tf_graph(tf_graph,
                             continue_on_error=args.continue_on_error,
                             verbose=args.verbose,
                             target=args.target)

    model_proto = g.make_model(
        "converted from {}".format(args.input), args.inputs, args.outputs)

    # write onnx graph
    if args.output:
        with open(args.output, "wb") as f:
            f.write(model_proto.SerializeToString())


main()
