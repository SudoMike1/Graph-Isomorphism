
from graph_io import *
from graph import *


def stable_coloring(graph):
    coloring = {v: 1 for v in graph.vertices}
    iterations = 0
    # print(f"\nGraph initial vertices: {len(graph.vertices)}")
    # print(f"Initial edges: {len(graph.edges)}")

    while True:
        new_coloring = {}
        color_info = {}

        if len(graph.edges) == 0 or all(len(v.neighbours) == len(graph.vertices[0].neighbours) for v in graph.vertices):
            if iterations == 0:
                neighborhood_signatures = {v: tuple(sorted([coloring[n] for n in v.neighbours])) for v in
                                           graph.vertices}
                return coloring, 0, neighborhood_signatures

        for v in graph.vertices:
            neighbor_colors = sorted([coloring[n] for n in v.neighbours])
            color_info[v] = (coloring[v], tuple(neighbor_colors))
            # print(f"Vertex {v}: color={coloring[v]}, neighbor_colors={neighbor_colors}")

        color_map = {}
        for index, color in enumerate(sorted(set(color_info.values()))):
            color_map[color] = index + 1

        for v in graph.vertices:
            new_coloring[v] = color_map[color_info[v]]

        if new_coloring == coloring:
            # print(f"Stabilized after {iterations} iterations: {coloring}")
            neighborhood_signatures = {v: tuple(sorted([coloring[n] for n in v.neighbours])) for v in graph.vertices}
            break

        coloring = new_coloring
        iterations += 1
        # print(f"Iteration {iterations}: {coloring}")

    return coloring, iterations, neighborhood_signatures


def basic_colorref(file_path):
    graphs = load_graphs_from_grl(file_path)
    colorings = []
    for index, graph in enumerate(graphs):
        # print(f"\nProcessing Graph {index}")
        coloring, iterations, neighborhood_signatures = stable_coloring(graph)

        unique_colors = set(coloring.values())
        color_classes = sorted([list(coloring.values()).count(color) for color in unique_colors])


        discrete = all(size == 1 for size in color_classes)

        # print(f"Final size: {max(coloring.values())}")
        # print(f"Final coloring: {sorted(coloring.values())}")

        colorings.append((index, color_classes, iterations, discrete, neighborhood_signatures))

    return group_equivalence_classes(colorings)


def load_graphs_from_grl(file_path):
    with open(file_path, 'r') as f:
        list_of_graphs, title = read_graph_list(Graph, f)
    return list_of_graphs


def group_equivalence_classes(colorings):
    equivalence_classes = {}

    for index, color_classes, iterations, discrete, neighborhood_signatures in colorings:

        key = (tuple(color_classes), iterations, discrete, tuple(sorted(neighborhood_signatures.values())))

        if key not in equivalence_classes:
            equivalence_classes[key] = []
        equivalence_classes[key].append(index)

    result = []
    for key, indices in equivalence_classes.items():
        sorted_indices = sorted(indices)
        result.append((sorted_indices, list(key[0]), key[1], key[2]))

    return result