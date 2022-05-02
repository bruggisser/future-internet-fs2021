import networkx as nx
import matplotlib.pyplot as plt
from csv import reader
import os
import ortoolslpparser


for x in range(0, 40):
    f = open("./myself/output/b/linearprogram{}.lp".format(x), "w")

    print("Progress: %.2f %%" % ((x / 39 * 100),))
    # create a multigraph containing all the flows
    G = nx.MultiDiGraph()
    # create a multigraph containing the network
    network_G = nx.DiGraph()

    demands = []
    with open('./ground_truth/input/a/demand{}.demand'.format(x)) as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            src = row[0]
            dst = row[1]
            demands.append((src, dst))

    # create the network based
    with open('./ground_truth/input/a/graph{}.graph'.format(x)) as read_obj:
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
    with open('./ground_truth/input/a/path{}.path'.format(x)) as read_obj:
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
                        if(k + 1 < len(paths)):
                            u, v = int(n), int(paths[k+1])
                            if(nx.has_path(network_G, u, v)):
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
                        str(capacity.get('capacity'))+';\n')

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
        "./myself/output/b/linearprogram{}.lp".format(x))
    solver = parse_result["solver"]
    solver.Solve()

    var_names = filter(lambda x: 'p' in x, list(parse_result["var_names"]))
    var_names = list(map(lambda x: int(x.replace('p_', '')), var_names))
    var_names = sorted(var_names)

    f = open("./myself/output/b/rate{}.rate".format(x), "w")

    for flow in var_names:
        f.write(str(solver.LookupVariable(
            'p_' + str(flow)).solution_value()) + '\n')
    f.close()
