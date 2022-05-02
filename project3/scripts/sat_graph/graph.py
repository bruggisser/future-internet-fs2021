import networkx as nx
from scripts import util
from scripts.sat_graph.dfs import find_paths


class Graph:
    def __init__(self):
        self.G = nx.Graph()
        # add nodes
        sat_positions = util.read_sat_positions(sat_pos_file)
        for sat in sat_positions:
            self.G.add_node(sat)
        city_positions = util.read_city_positions(city_pos_file)
        for city in city_positions:
            self.G.add_node(city)

        self.valid_isls = util.read_valid_isls(valid_isls_file)
        self.city_coverage = util.read_coverage(city_coverage_file)

    def add_isls(self):
        # add edges
        for sat1, sat2 in self.valid_isls:
            self.G.add_edge(sat1, sat2, length=self.valid_isls[sat1, sat2])

    def add_city_links(self):
        # add edges
        for city, sat in self.city_coverage:
            self.G.add_edge(city, sat, length=self.city_coverage[city, sat])

    def find_path(self, src):
        return find_paths(self.G, src)

    def remove_link(self, src, dest):
        if self.G.has_edge(src, dest):
            dist = self.G.get_edge_data(src, dest)['length']
            self.G.remove_edge(src, dest)
            return dist
        return -1

    def add_link(self, src, dest, dist, restricted=False):
        if not self.G.has_edge(src, dest) and (not restricted or (self.G.degree(src) < 4 and self.G.degree(dest) < 4)):
            self.G.add_edge(src, dest, length=dist)

    def check_path(self, path):
        if len(path) > 2 and (not self.G.has_edge(path[1], path[2]) and self.G.degree(path[1]) >= 4):
            return path[1], path[2]
        for i in range(1, len(path) - 2):
            if path[i + 1] >= 10000:
                continue
            if not self.G.has_edge(path[i], path[i + 1]) and not self.G.has_edge(path[i + 1], path[i + 2]):
                if self.G.degree(path[i + 1]) >= 3:
                    return path[i], path[i + 1]
        return -1, -1

    def update_node(self, other, node):
        self_nodes = self.G.neighbors(node)
        other_nodes = other.G.neighbors(node)
        remove = []
        for n in self_nodes:
            if n >= 10000:
                continue
            found = False
            for o in other_nodes:
                if o == n:
                    found = True
                    break
            if not found:
                remove.append([node, n])
        for node, n in remove:
            self.remove_link(node, n)

    def find_distance(self, src, target):
        try:
            path = nx.dijkstra_path(self.G, src, target, weight='length')
            path_len = 0
            for n in range(0, len(path) - 1):
                link_len = 0
                if path[n] < 10000 and path[n + 1] < 10000:
                    link_len = self.valid_isls[path[n], path[n + 1]]
                else:
                    if path[n] > 10000:
                        link_len = self.city_coverage[path[n], path[n + 1]]
                    else:
                        link_len = self.city_coverage[path[n + 1], path[n]]
                path_len += link_len
            return path_len
        except:
            return 1000000000


sat_pos_file = "../../input_data/sat_positions.txt"
city_pos_file = "../../input_data/cities.txt"
city_coverage_file = "../../input_data/city_coverage.txt"
valid_isls_file = "../../input_data/valid_isls.txt"
