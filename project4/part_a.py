import networkx as nx
import matplotlib.pyplot as plt
from csv import reader
import os

for x in range(0, 40):
    print("Progress: %.2f %%" % ((x / 39 * 100),))
    # create a multigraph containing all the flows
    G = nx.MultiDiGraph()
    # create a multigraph containing the network
    network_G = nx.DiGraph()

    # store the current demands
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

    # read out the number of nodes in the network
    N = len(G.nodes)

    # flows and their capacities / rates
    flows = []
    rates = {}

    with open('./ground_truth/input/a/path{}.path'.format(x)) as read_obj:
        csv_reader = reader(read_obj)
        for i, row in enumerate(csv_reader):
            paths = row[0].split('-')
            for demand in demands:
                # only add the flow / path to the Graph if we have a demand along it
                if demand[0] == paths[0] and demand[1] == paths[len(paths) - 1]:
                    for k, n in enumerate(paths):
                        if(k + 1 < len(paths)):
                            if(nx.has_path(network_G, int(n), int(paths[k+1]))):
                                G.add_edge(int(n), int(
                                    paths[k+1]), key=i, flow=i)
                            else:
                                print("Invalid flow")
                                rates[i] = 0
                # if there is no demand then set the rate to 0
                else:
                    rates[i] = 0

    # print(G.nodes)
    # print(network_G.get_edge_data(0, 1))

    # as long as there are flows in the network
    while(len(G.edges) > 0):
        min_edge = None
        node_pair = None

        # go through all possible edges
        for i in range(0, N):
            for j in range(0, N):
                nodes = G.get_edge_data(i, j)
                data = network_G.get_edge_data(i, j)
                if not data or not nodes:
                    continue
                # get number of such edges that go from i to j
                nodes = nodes.keys()
                if(not min_edge or data['capacity']/len(nodes) < min_edge):
                    min_edge = data['capacity']/len(nodes)
                    node_pair = (i, j)

        # get all flows that use that link
        flows = G.get_edge_data(node_pair[0], node_pair[1])
        flows = flows.values()
        # need to remove all the flows that share the same link
        # and allocate them the appropriate rate
        flows = list(map(lambda x: x.get('flow'), flows))
        for flow in flows:
            if rates.get(flow):
                pass
            else:
                rates[flow] = min_edge
                to_remove = [(i, j, k) for i, j, k in G.edges if k == flow]
                for edge in to_remove:
                    current_cap = network_G[edge[0]][edge[1]]['capacity']
                    new_cap = current_cap - min_edge
                    network_G[edge[0]][edge[1]]['capacity'] = new_cap
                    G.remove_edge(edge[0], edge[1], key=flow)

    f = open("./myself/output/a/rate{}.rate".format(x), "w")
    for key in sorted(rates):
        f.write(str(rates[key]) + "\n")
    f.close()
