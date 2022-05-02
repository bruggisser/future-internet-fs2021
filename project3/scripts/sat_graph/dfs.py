from heapq import heappush, heappop


def find_paths(graph, src):
    nodes = {src: {'dist': 0, 'hops': 0}}
    queue = []
    heappush(queue, (0, src))
    # find distances
    while len(queue) > 0:
        current = heappop(queue)[1]
        node = nodes[current]
        for edge in graph.edges(current):
            target = edge[1]
            if target in nodes:
                old_dist = nodes[target]['dist']
                old_hops = nodes[target]['hops']
                new_dist = 0
                try:
                    new_dist = graph.get_edge_data(*edge)['length'] + node['dist']
                except:
                    print(f"failed for {current} - {target}")
                    exit()
                new_hops = node['hops'] + 1
                if new_dist / max(old_dist, 1) + new_hops - old_hops < 1:
                    nodes[target] = {'dist': new_dist, 'hops': new_hops}
                    heappush(queue, (new_dist, target))
            else:
                nodes[target] = {'dist': graph.get_edge_data(*edge)['length'] + node['dist'], 'hops': node['hops'] + 1}
                heappush(queue, (nodes[target]['dist'], target))

    # extract paths
    paths = {}
    for city in range(10001, 10101):
        path = [city]
        current = city
        while current != src:
            if current not in nodes:
                break
            for edge in graph.edges(current):
                target = edge[1]
                dist = graph.get_edge_data(*edge)['length']
                c_dist = nodes[current]['dist']
                c_hops = nodes[current]['hops']
                if nodes[target]['hops'] + 1 == c_hops and nodes[target]['dist'] + dist == c_dist:
                    path.append(target)
                    current = target
                    break
        path.reverse()
        paths[city] = path

    return paths
