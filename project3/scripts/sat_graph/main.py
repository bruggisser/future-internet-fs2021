from networkx import NetworkXNoPath

from graph import Graph
from scripts import util
import datetime

# create graphs
full_graph = Graph()
partial_graph = Graph()
empty_graph = Graph()

full_graph.add_isls()
full_graph.add_city_links()

partial_graph.add_city_links()

city_pos_file = "../../input_data/cities.txt"
city_pair_file = "../../input_data/city_pairs.txt"
cities = util.read_city_positions(city_pos_file)
city_pairs = util.read_city_pairs(city_pair_file)

start = datetime.datetime.now()


ALLOWED_OFFSET = 1.05

city_city_map = []

for city in cities:
    print(city)

    paths = full_graph.find_path(city)
    for target in cities:
        if target <= city:
            continue

        path = paths[target]
        check_src, check_dest = full_graph.check_path(path)
        if check_src != -1 and partial_graph.find_distance(city, target) <= ALLOWED_OFFSET * city_pairs[city, target]:
            continue

        for i in range(1, len(path) - 2):
            # add path to links
            if path[i] < 10000 and path[i + 1] < 10000:
                empty_graph.add_link(path[i], path[i + 1], 0, True)
                dist = 0
                try:
                    dist = full_graph.G.get_edge_data(path[i], path[i + 1])['length']
                except:
                    dist = 0
                partial_graph.add_link(path[i], path[i + 1], dist)
            # if all links are used, remove unused links from full_graph
            if empty_graph.G.degree(path[i]) == 4:
                full_graph.update_node(empty_graph, path[i])
        if empty_graph.G.degree(path[len(path) - 1]) == 4:
            full_graph.update_node(empty_graph, path[len(path) - 1])

with open("../../output_data/sat_links.txt", "w") as f:
    for link in empty_graph.G.edges:
        if link[0] < 10000 and link[1] < 10000:
            f.write("{},{}\n".format(link[0], link[1]))
print(len(empty_graph.G.edges))
print(f"{start} to {datetime.datetime.now()}")
