import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx


def avg_path_length(G: nx.Graph) -> float:
    running_total = 0

    for edge in G.edges(data=True):
        running_total += G.edges()[edge]["distance"]

    return running_total / len(G.edges())


def gen_index_string(source, state, method, net_name):
    outstring = ""
    if "bk" in str(source):
        outstring += "bk"
    else:
        outstring += "gw"

    iteration_number = net_name.replace(".", "_")
    iteration_number = iteration_number.split("_")[2]

    return "_".join([outstring, state, method, iteration_number])


data_source_bk = Path("./trial_outputs/20Nov2025bk/")
data_source_gw = Path("./trial_outputs/20Nov2025gw/")

series_entry_template = {
    "data_source": None,
    "state": None,
    "num_nodes": None,
    "num_edges": None,
    "method": None,
    "APL_original": None,
    "APL_perturbed": None,
    "APL_std": None,
    "btwn_original": None,
    "btwn_perturbed": None,
    "btwn_std": None,
    "clust_original": None,
    "clust_perturbed": None,
    "clust_std": None,
    "mod_original": None,
    "mod_perturbed": None,
}

analysis: pd.DataFrame = pd.read_csv("./Analysis/20Nov2025_amended.csv", index_col=0)

for source in [data_source_bk, data_source_gw]:
    for state in os.listdir(source):
        for method in os.listdir(Path(source / state)):
            with Path(source / state / method / "original_network.pkl").open("rb") as f:
                original_network = pickle.load(f)

            old_btwn = nx.betweenness_centrality(original_network, weight="distance")
            old_clustering = nx.clustering(original_network, weight="distance")
            old_mod = nx.community.modularity(original_network, weight="distance", communities=nx.community.label_propagation_communities(original_network))

            all_entries = []
            for net_name in os.listdir(Path(source / state / method)):
                if "original" in net_name:
                    continue

                index_string = gen_index_string(source, state, method, net_name)
                if index_string in analysis.index:
                    continue

                print(index_string)

                entry = series_entry_template.copy()
                with Path(source / state / method / net_name).open("rb") as f:
                    jittered_net = pickle.load(f)

                try:
                    entry["data_source"] = "gw" if source == data_source_gw else "bk"
                    entry["state"] = state
                    entry["num_nodes"] = len(jittered_net.nodes())
                    entry["num_edges"] = len(jittered_net.edges())
                    entry["method"] = method
                    entry["APL_original"] = np.mean([d for (_, _, d) in original_network.edges.data("distance")])
                    entry["APL_perturbed"] = np.mean([d for (_, _, d) in jittered_net.edges.data("distance")])
                    entry["APL_std"] = np.std([d - original_network.edges[u, v]["distance"] for (u, v, d) in jittered_net.edges.data("distance")])

                    new_btwn = nx.betweenness_centrality(jittered_net, weight="distance")
                    entry["btwn_original"] = np.mean([*old_btwn.values()])
                    entry["btwn_perturbed"] = np.mean([*new_btwn.values()])
                    entry["btwn_std"] = np.std([new_btwn[node] - old_btwn[node] for node in new_btwn.keys()])

                    new_clustering = nx.clustering(jittered_net, weight="distance")
                    entry["clust_original"] = np.mean([*old_clustering.values()])
                    entry["clust_perturbed"] = np.mean([*new_clustering.values()])
                    entry["clust_std"] = np.std([new_clustering[node] - old_clustering[node] for node in new_clustering.keys()])

                    new_mod = nx.community.modularity(jittered_net, weight="distance", communities=nx.community.label_propagation_communities(jittered_net))
                    entry["mod_original"] = old_mod
                    entry["mod_perturbed"] = new_mod

                    analysis.loc[index_string] = entry
                except KeyError as e:
                    continue

print(analysis.head(5))
Path("./Analysis/20Nov2025.csv").touch()
analysis.to_csv("./Analysis/20Nov2025_amended.csv", columns=analysis.columns.tolist())
