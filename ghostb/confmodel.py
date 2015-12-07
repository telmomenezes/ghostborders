import graph


def normalize_with_confmodel(csv_in, csv_out, runs):
    graph = graph.read_graph(csv_in)
    ref_graph = graph.conf_model_n_times(graph, runs)
    graph.normalize(graph, ref_graph)
    graph.write_graph(graph, csv_out)
