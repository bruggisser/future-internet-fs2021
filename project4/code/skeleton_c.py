# The MIT License (MIT)
#
# Copyright (c) 2019 Simon Kassing (ETH)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from _csv import reader
import multiprocessing
import networkx
from random import shuffle
from ortoolslpparser import ortoolslpparser

try:
    import wanteutility
except (ImportError, SystemError):
    import wanteutility

try:
    import assignment_parameters
except (ImportError, SystemError):
    import assignment_parameters

MAX_NUM_PATHS = 10


def solve(in_graph_filename, in_demands_filename, out_paths_filename, out_rates_filename, lp_filename):
    # Read in input
    print("find paths", in_graph_filename)
    graph = wanteutility.read_graph(in_graph_filename)
    with open(out_paths_filename, "w+") as rate_file:
        for i in graph.nodes:
            for j in graph.nodes:
                if i == j:
                    continue
                all_paths = []
                paths = networkx.edge_disjoint_paths(
                    graph, i, j, cutoff=5)
                count = 0
                paths = list(paths)
                if len(paths) < MAX_NUM_PATHS:
                    all_paths = networkx.all_simple_paths(
                        graph, i, j, cutoff=4)
                    all_paths = list(all_paths)
                    shuffle(all_paths)
                for path in paths:
                    if count < MAX_NUM_PATHS:
                        rate_file.write("-".join(map(str, path)) + "\n")
                        count = count + 1
                    else:
                        break
                for path in all_paths:
                    if count < MAX_NUM_PATHS:
                        rate_file.write("-".join(map(str, path)) + "\n")
                        count = count + 1
                    else:
                        break

    print("solve lp", in_graph_filename)
    # from part B
    f = open(lp_filename, "w")

    # create a multigraph containing all the flows
    G = networkx.MultiDiGraph()
    # create a multigraph containing the network
    network_G = networkx.DiGraph()

    demands = []
    with open(in_demands_filename) as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            src = row[0]
            dst = row[1]
            demands.append((src, dst))

    # create the network based
    with open(in_graph_filename) as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            u, v = int(row[0]), int(row[1])
            capacity = float(row[2])
            # add the nodes to both graphs
            for n in [u, v]:
                G.add_node(n)
                network_G.add_node(n)
            # add the network link with capacity to the network graph
            network_G.add_edge(u, v, capacity=capacity)

    # flows and their capacities / rates
    flows = []
    paths = []
    rates = {}

    f.write("max: Z;\n")

    paths_to_consider = []
    with open(out_paths_filename) as read_obj:
        csv_reader = reader(read_obj)
        for i, row in enumerate(csv_reader):
            paths = row[0].split('-')
            has_demand = False
            for demand in demands:
                # only add the flow / path to the Graph if we have a demand along it
                if demand[0] == paths[0] and demand[1] == paths[len(paths) - 1]:
                    has_demand = True
                    paths_to_consider.append(
                        {'src': int(demand[0]), 'dst': int(demand[1]), 'flow': i})
                    for k, n in enumerate(paths):
                        if (k + 1 < len(paths)):
                            u, v = int(n), int(paths[k + 1])
                            if (networkx.has_path(network_G, u, v)):
                                G.add_edge(u, v, key=i, flow=i)
                            else:
                                print("Invalid flow")
                                rates[i] = 0

            if not has_demand:
                f.write('p_{}= 0;\n'.format(i))
            else:
                f.write('p_{} >= 0;\n'.format(i))

    for i in range(0, len(G.nodes)):
        for j in range(0, len(G.nodes)):
            flows = G.get_edge_data(i, j)
            capacity = network_G.get_edge_data(i, j)
            if flows:
                flows = flows.keys()
                flows = list(map(lambda x: 'p_' + str(x), flows))
                f.write(' + '.join(flows) + ' <= ' +
                        str(capacity.get('capacity')) + ';\n')

    # for flow in flows: q
    for i in range(0, len(G.nodes)):
        for j in range(0, len(G.nodes)):
            flows = [d for d in paths_to_consider if d['src']
                     == i and d['dst'] == j]
            # print(flows)
            if len(flows):
                flows = list(map(lambda x: 'p_' + str(x['flow']), flows))
                f.write(' + '.join(flows) + ' - Z >= 0;\n')
    f.close()

    parse_result = ortoolslpparser.parse_lp_file(
        lp_filename)
    solver = parse_result["solver"]
    solver.Solve()

    var_names = filter(lambda x: 'p' in x, list(parse_result["var_names"]))
    var_names = list(map(lambda x: int(x.replace('p_', '')), var_names))
    var_names = sorted(var_names)

    f = open(out_rates_filename, "w")

    for flow in var_names:
        f.write(str(solver.LookupVariable(
            'p_' + str(flow)).solution_value()) + '\n')
    f.close()


def run(appendix):
    solve(
        "../ground_truth/input/c/graph%d.graph" % appendix,
        "../ground_truth/input/c/demand.demand",
        "../myself/output/c/path%d.path" % appendix,
        "../myself/output/c/rate%d.rate" % appendix,
        "../myself/output/c/linearprogram%d.lp" % appendix
    )


def main():
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(run, range(assignment_parameters.num_tests_c))

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
