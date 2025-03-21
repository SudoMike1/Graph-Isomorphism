from operator import index

from graph_io import *
from graph import *





def get_coloring_classes_sizes(colors):
    size_of_color_classes = {}
    for color in colors:
        if color in size_of_color_classes:
            size_of_color_classes[color] += 1
        else:
            size_of_color_classes[color] = 1
    return size_of_color_classes



def branching_search(graph1: Graph, graph2: Graph, colors1: dict, colors2: dict) -> bool:
    color_sizes_g1 = get_coloring_classes_sizes(colors1)
    all_colors = list(colors1.values()) + list(colors2.values())
    unique_colors = set(all_colors)
    biggest_color_class_g1 = max(color_sizes_g1)

    chosen_vertex_g1 = None
    possible_mapping = []

    for v1, v2 in zip(colors1, colors2):
        if colors1[v1] == biggest_color_class_g1 and chosen_vertex_g1 is None:
            chosen_vertex_g1 = v1

        if colors2[v2] == biggest_color_class_g1:
            possible_mapping.append(v2)

    for vertex in possible_mapping:
        new_colors1 , new_colors2 = colors1.copy() , colors2.copy()
        new_colors1[vertex], new_colors2[chosen_vertex_g1] = max(unique_colors) + 1










    """
    Stub for branching search algorithm.
    :param graph1: First graph.
    :param graph2: Second graph.
    :param colors1: Node color mapping for first graph.
    :param colors2: Node color mapping for second graph.
    :return: True if graphs are isomorphic, otherwise False.
    """
    # Placeholder: Implement branching rules here
    return True  # Defaulting to True for now




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




def get_final_coloring(all_graphs):
    all_vs = []

    for i, graph in enumerate(all_graphs):
        all_vs.extend(graph.vertices)

    current_coloring = {}
    for v in all_vs:
        current_coloring[v] = 1

    degree_to_color = {}
    next_col = 1

    for v in all_vs:
        current_n_count = len(v.neighbours)
        if current_n_count not in degree_to_color:
            degree_to_color[current_n_count] = next_col
            next_col += 1
        current_coloring[v] = degree_to_color[current_n_count]
    while True:
        new_colouring = {}

        # maps old colors to a list of vertices with that color
        old_mapping = {}

        for v in all_vs:
            old_color = current_coloring[v]

            # need to check if this color is in old mapping, if not create it, and add it
            if old_color not in old_mapping:
                old_mapping[old_color] = []

            old_mapping[old_color].append(v)

        next_col = 1

        # (neighborprofile > color)
        neighbors_to_color_list = []
        for old_col in sorted(old_mapping.keys()):
            vertices_grouped = old_mapping[old_col]

            for v in vertices_grouped:
                neighbour_colors = []

                for current_neighbour in v.neighbours:
                    neighbour_colors.append(current_coloring[current_neighbour])

                neighbour_colors.sort()
                current_profile = tuple(neighbour_colors)

                # include old col so different colors but same neighborhood profile remain distinct
                full_profile = (old_col, current_profile)

                assigned_color = None
                for (existing_profile, existing_col) in neighbors_to_color_list:
                    if full_profile == existing_profile:
                        assigned_color = existing_col
                        break

                if assigned_color is None:
                    assigned_color = next_col
                    next_col += 1
                    neighbors_to_color_list.append((full_profile, assigned_color))

                new_colouring[v] = assigned_color

        # need to check if coloring is the same
        if new_colouring != current_coloring:
            current_coloring = new_colouring
        else:
            break

    return current_coloring