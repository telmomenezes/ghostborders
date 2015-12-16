import ghostb.graph as graph


def normalize_with_confmodel(csv_in, csv_out, runs):
    g = graph.read_graph(csv_in)
    ref_graph = graph.conf_model_n_times(g, runs)
    graph.normalize(g, ref_graph)
    graph.write_graph(g, csv_out)
