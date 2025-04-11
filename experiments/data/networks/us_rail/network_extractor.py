import networkx as nx
import csv
import math
import pickle
import matplotlib.pyplot as plt


def distance(coord1, coord2):
    lat1, long1 = coord1
    lat2, long2 = coord2
    return math.sqrt((lat1 - lat2) ** 2 + (long1 - long2) ** 2)

def gen_graph(filename):
    '''
    OBJECTID,FRANODEID,COUNTRY,STATE,STFIPS,CTYFIPS,STCYFIPS,FRADISTRCT,PASSNGR,PASSNGRSTN,BNDRY,x,y
    1,300000,US,HI,15,009,15009,7,,,0,-156.689726458522,20.936530276911
    '''

    G = nx.Graph()
    nodes = {}
    coordinates = []

    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        count = 0
        for row in reader:
            # Use OBJECTID as the node identifier.
            node_id = int(row["OBJECTID"])
            # In the CSV, 'x' is longitude and 'y' is latitude.
            lat = float(row["y"])
            long = float(row["x"])
            nodes[node_id] = (lat, long)
            coordinates.append((lat, long, node_id))
            G.add_node(node_id, lat=lat, long=long)

            count += 1

    print("Read graph data")

    # For each node, find the two closest neighbors and then connect to up to two more neighbors
    # within 10% above the farthest distance of the two closest.
    count = 0
    total = len(nodes)
    chunk = total // 10
    print(f"Processing {total} nodes.")

    coordinates.sort()

    for i, (lat, long, node_id) in enumerate(coordinates):

        searching_neighbors = True
        offset = 0
        closest_neighbors = []
        while searching_neighbors:
            offset = offset + 1

            j = i + offset
            if j < len(coordinates):
                j_lat, j_long, j_node_id = coordinates[j]

                # if we are already too far on just latitude to find new partners,
                # leave.
                if len(closest_neighbors) > 1 and abs(j_lat - lat) > closest_neighbors[1][1]:
                    searching_neighbors = False

                    continue

                distance_j = distance((lat, long), (j_lat, j_long))

                # maintain list of 2 closest in first two spots, add if
                # any are within 10% of 2nd closest so far
                if len(closest_neighbors) < 2:
                    closest_neighbors.append((j_node_id, distance_j))
                    closest_neighbors.sort(key = lambda x: x[1])

                elif distance_j < closest_neighbors[0][1]:
                    closest_neighbors.insert(0, (j_node_id, distance_j))
                elif distance_j < closest_neighbors[1][1]:
                    closest_neighbors.insert(1, (j_node_id, distance_j))
                elif distance_j < closest_neighbors[1][1] * 1.1:
                    closest_neighbors.append((j_node_id, distance_j))

            # j index out of bounds
            else:
                searching_neighbors = False

        # Add edge
        for other_id, d in closest_neighbors[:2]:
            G.add_edge(node_id, other_id, dist=d)

        if len(closest_neighbors) > 1:
            # Add up to 2 other nodes that are within 10% of distance to second closest
            extras = 0
            threshold = 1.1 * closest_neighbors[1][1]
            for other_id, d in closest_neighbors[2:]:
                if d <= threshold:
                    G.add_edge(node_id, other_id, dist=d)
                    extras += 1
                if extras == 2:
                    break

    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    positions = {key:(value[1], value[0]) for key, value in nodes.items()}
    nx.draw(G, positions)
    plt.show()

    with open("outfile", 'wb') as out:
        pickle.dump(G, out)

    return G

if __name__ == "__main__":

    '''
    OBJECTID,FRANODEID,COUNTRY,STATE,STFIPS,CTYFIPS,STCYFIPS,FRADISTRCT,PASSNGR,PASSNGRSTN,BNDRY,x,y
    1,300000,US,HI,15,009,15009,7,,,0,-156.689726458522,20.936530276911
    '''
    railfile = "NTAD_North_American_Rail_Network_Nodes_1238521289684721083.csv"
    g = gen_graph(railfile)

    # with open("outfile", 'rb') as infile:
    #     g = pickle.load(infile)
    # positions = {node:(g.nodes[node]['long'],g.nodes[node]['lat']) for node in g.nodes}
    # nx.draw(g, positions)
    # plt.show()