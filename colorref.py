from operator import index

from graph_io import *
from graph import *



def is_discrete(color_classes):
    # for vertex in color_classes:
    #     if color_classes[vertex] != 1:
    #         return False
    # return True
    return len(set(color_classes.values())) == len(color_classes)

def get_coloring_classes_sizes(colors):
    size_of_color_classes = {}
    for color in colors:
        if color in size_of_color_classes:
            size_of_color_classes[color] += 1
        else:
            size_of_color_classes[color] = 1
    return size_of_color_classes



def branching_search(graph1: Graph, graph2: Graph, colors1: dict, colors2: dict) -> bool:
    """
        Stub for branching search algorithm.
        :param graph1: First graph.
        :param graph2: Second graph.
        :param colors1: Node color mapping for first graph.
        :param colors2: Node color mapping for second graph.
        :return: True if graphs are isomorphic, otherwise False.
    """

    color_sizes_g1 = get_coloring_classes_sizes(colors1)
    all_colors = list(colors1.values()) + list(colors2.values())
    unique_colors = set(all_colors)
    biggest_color_class_g1 = max(color_sizes_g1, key=color_sizes_g1.get)

    chosen_vertex_g1 = None
    possible_mapping = []

    for v1 in graph1.vertices:
        if colors1[v1] == biggest_color_class_g1 and chosen_vertex_g1 is None:
            chosen_vertex_g1 = v1
            break
    for v2 in graph2.vertices:
        if colors2[v2] == biggest_color_class_g1:
            possible_mapping.append(v2)

    print(possible_mapping)

    # we loop through all the vertices that are a possible match
    for vertex_g2 in possible_mapping:
        new_colors1 , new_colors2 = colors1.copy() , colors2.copy()
        new_color = max(all_colors) + 1
        new_colors1[chosen_vertex_g1] = new_color
        new_colors2[vertex_g2] = new_color
        # new_colors1[chosen_vertex_g1], new_colors2[vertex_g2] = max(unique_colors) + 1

        all_vertices_colors = {}
        for vertex, color in new_colors1.items():
            all_vertices_colors[vertex] = color
        for vertex, color in new_colors2.items():
            all_vertices_colors[vertex] = color

        print("Trying mapping: G1 vertex", chosen_vertex_g1, "→ G2 vertex", vertex_g2)
        print("Before refinement:", new_colors1)
        print("After refinement:", coloring_g1, coloring_g2)

        # we refine the coloring of both graphs
        coloring = get_final_coloring(graph1, graph2, all_vertices_colors)

        print("Trying mapping: G1 vertex", chosen_vertex_g1, "→ G2 vertex", vertex_g2)
        print("Before refinement:", new_colors1)
        print("After refinement:", coloring_g1, coloring_g2)

        #if the coloring after the refinement is the same: we do go deeper in this branch
        #else : we finish exploring this branch
        coloring_g1 = {v: color for v, color in coloring.items() if v in graph1.vertices}
        coloring_g2 = {v: color for v, color in coloring.items() if v in graph2.vertices}

        if coloring_g1[chosen_vertex_g1] != coloring_g2[vertex_g2]:
            continue

        if get_coloring_classes_sizes(coloring_g1) == get_coloring_classes_sizes(coloring_g2):
            if is_discrete(coloring_g1):
                print("is discrete")
                return True
            else:
                print("else")
                if branching_search(graph1, graph2, coloring_g1, coloring_g2):
                    print("if branching search")
                    return True
    return False


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
        for i, color in enumerate(sorted(set(color_info.values()))):
            color_map[color] = i + 1

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

# def basic_colorref(file_path):
#     graphs = load_graphs_from_grl(file_path)
#
#     colorings = []
#
#     for i, graph in enumerate(graphs):
#         # print(f"\nProcessing Graph {index}")
#         coloring, iterations, neighborhood_signatures = stable_coloring(graph)
#
#         unique_colors = set(coloring.values())
#         color_classes = sorted([list(coloring.values()).count(color) for color in unique_colors])
#
#
#         discrete = all(size == 1 for size in color_classes)
#
#         # print(f"Final size: {max(coloring.values())}")
#         # print(f"Final coloring: {sorted(coloring.values())}")
#
#         colorings.append((i, color_classes, iterations, discrete, neighborhood_signatures))
#
#     return group_equivalence_classes(colorings)


def load_graphs_from_grl(file_path):
    with open(file_path) as f:
        read, _ = read_graph_list(Graph, f)
    return read


def group_equivalence_classes(colorings):
    equivalence_classes = {}

    for index_i, color_classes, iterations, discrete, neighborhood_signatures in colorings:

        key = (tuple(color_classes), iterations, discrete, tuple(sorted(neighborhood_signatures.values())))

        if key not in equivalence_classes:
            equivalence_classes[key] = []
        equivalence_classes[key].append(index_i)

    results = []
    for key, indices in equivalence_classes.items():
        sorted_indices = sorted(indices)
        results.append((sorted_indices, list(key[0]), key[1], key[2]))

    return results




def get_final_coloring(graph1, graph2 , all_vertices_colors):
    # Combine vertices from both graphs

    all_vs = list(graph1.vertices) + list(graph2.vertices)

    # Initialize colors (all start with 1)
    current_coloring = all_vertices_colors



    while True:
        new_coloring = {}
        old_mapping = {}

        # Group vertices by color
        for v in all_vs:
            color = current_coloring[v]
            old_mapping.setdefault(color, []).append(v)

        next_col = 1
        neighbors_to_color_list = []

        for old_col in sorted(old_mapping.keys()):
            vertices_grouped = old_mapping[old_col]

            for v in vertices_grouped:
                neighbor_colors = sorted(current_coloring[n] for n in v.neighbours)
                full_profile = (old_col, tuple(neighbor_colors))

                assigned_color = None
                for existing_profile, existing_col in neighbors_to_color_list:
                    if full_profile == existing_profile:
                        assigned_color = existing_col
                        break

                if assigned_color is None:
                    assigned_color = next_col
                    next_col += 1
                    neighbors_to_color_list.append((full_profile, assigned_color))

                new_coloring[v] = assigned_color

        if new_coloring == current_coloring:
            break  # Stop when no further refinement occurs
        current_coloring = new_coloring

    return current_coloring


def basic_colorref(all_graphs):
    graphs = load_graphs_from_grl(all_graphs)
    result = []

    # assigning initial color
    for graph in graphs:
        for vertex in graph.vertices:
            vertex.colornum = len(vertex.neighbours)

    # loop that will run till color refinement stabilizes
    stable = False
    while not stable:
        stable = True
        new_colors = {}

        # find neighbours and signature the vertices
        for graph in graphs:
            for vertex in graph.vertices:
                neighbour_colors = []
                for n in vertex.neighbours:
                    neighbour_colors.append(n.colornum)
                neighbour_colors.sort()
                signature = (vertex.colornum, tuple(neighbour_colors))
                new_colors[vertex] = signature

        colors = {}
        next_color = 0
        # assign new values to unique signatured ones
        for vertex in new_colors:
            signature = new_colors[vertex]
            if signature not in colors:
                colors[signature] = next_color
                next_color += 1

        # update each vertex baesd on colors
        for vertex in new_colors:
            new_color = colors[new_colors[vertex]]
            if new_color != vertex.colornum:
                stable = False
            vertex.colornum = new_color

    # signature for each graph
    signature_graph = {}
    for i, graph in enumerate(graphs):
        signature = []
        for v in graph.vertices:
            signature.append(v.colornum)
        signature.sort()
        signature = tuple(signature)

        # grroup identical signatured graphs
        if signature not in signature_graph:
            signature_graph[signature] = []
        signature_graph[signature].append(i)

    # size of each color and store in color class
    for signature, index in signature_graph.items():
        color_class = []
        for color in set(signature):
            color_class.append(signature.count(color))
        color_class.sort()

        # formatting
        is_discrete = len(set(signature)) == len(signature)
        iterations = count_iterations(graphs[index[0]])
        result.append((sorted(index), color_class, iterations, is_discrete))

    return result


def count_iterations(graph):
    vertex_index = list(graph.vertices)
    color = [1] * len(vertex_index)
    stable = False
    counter = 0

    while not stable:
        new_color = [0] * len(vertex_index)
        type_color = {}

        for v in vertex_index:
            neighbour_colors = []
            for n in v.neighbours:
                neighbour_colors.append(color[vertex_index.index(n)])
            neighbour_colors.sort()

            signature = tuple(neighbour_colors)
            if signature not in type_color:
                type_color[signature] = len(type_color) + 1
            new_color[vertex_index.index(v)] = type_color[signature]

        if new_color == color:
            stable = True

        else:
            color = new_color
            counter += 1

    if counter == 0:
        counter = 1

    return counter

if __name__ == "__main__":
    path = "/Users/nazhashas/Downloads/SampleGraphSetBranching/bigtrees1.grl"
    result = basic_colorref(path)
    print(result)


list_of_graphs = load_graphs_from_grl(path)
coloring0 = stable_coloring(list_of_graphs[0])[0]
# print(stable_coloring(list_of_graphs[3])[2])
# print(coloring0)
coloring3 = stable_coloring(list_of_graphs[2])[0]
# print(stable_coloring(list_of_graphs[3])[2])
# print(coloring3)
print(branching_search(list_of_graphs[0],list_of_graphs[2] , coloring0, coloring3))
# for equivalence_class in result:
#     for graph_indices in equivalence_class:
#         print(branching_search())

