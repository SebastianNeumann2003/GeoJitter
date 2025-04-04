import networkx as nx
import csv
import math
import pickle
import matplotlib.pyplot as plt


def gen_graph(edges, locations_filename):

    G = nx.Graph()

    with open(edges,"r") as edge_file:
        for line in edge_file.readlines():
            i,j = line.split()
            G.add_edge(int(i),int(j))

    print("Read graph data")
    total = len(G.nodes)
    print(f"Processing {total} nodes.")

    locations = {}

    with open(locations_filename,"r") as location_file:
        for line in location_file.readlines():
            fields = line.split()

            if len(fields) < 4:
                continue

            node = int(fields[0])
            lat = float(fields[2])
            long = float(fields[3])

            if lat == 0 or long == 0:
                continue

            if node in locations:
                a_lat, a_long, n = locations[node]
                n = n + 1
                u_long = a_long + (long - a_long)/n
                u_lat = a_lat + (lat - a_lat)/n
                locations[node] = (u_lat, u_long, n)
            else:
                locations[node] = (lat, long, 1)

    for node in locations:
        G.nodes[node]['lat'] = locations[node][0]
        G.nodes[node]['long'] = locations[node][1]

    # Trim nodes without location data
    nodes = list(G.nodes.keys())
    for node in nodes:
        if node not in locations:
            G.remove_node(node)

    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    positions = {node:(G.nodes[node]['long'],G.nodes[node]['lat']) for node in G.nodes}
    nx.draw(G, positions)
    plt.show()

    with open("spatial_graph", 'wb') as out:
        pickle.dump(G, out)

    return G

if __name__ == "__main__":

    '''
        0       2010-10-06T16:56:40Z    39.752713       -104.996337     2ef143e12038c870038df53e0478cefc

        0       2010-10-06T03:33:07Z    39.827022       -105.143191     f6f52a75fd80e27e3770cd3a87054f27

        0       2010-10-06T00:19:01Z    39.685683       -104.939221     dcc06bf19e775f436c2225be50e14922
    '''

    edges = "Brightkite_edges.txt"
    locations = "Brightkite_totalCheckins.txt"
    g = gen_graph(edges, locations)

    # with open("outfile", 'rb') as infile:
    #     g = pickle.load(infile)
    # positions = {node:(g.nodes[node]['long'],g.nodes[node]['lat']) for node in g.nodes}
    # nx.draw(g, positions)
    # plt.show()