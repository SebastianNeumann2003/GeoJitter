import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp


def load_network_and_regions(network_path: str, region_path: str):
    """
    Load the network and corresponding region shapefile.

    Args:
        network_path (str): Path to the network dataset.
        region_path (str): Path to the region shapefile.

    Returns:
        networkx.Graph: The loaded network.
        geopandas.GeoDataFrame: The loaded region data.
    """
    pass


def filter_network_by_subregion(network: nx.Graph, regions, filter_criteria):
    """
    Filter the network by specific subregions.

    Args:
        network (nx.Graph): The network to filter.
        regions: The regions to filter by.
        filter_criteria: A function that takes a node and regions and determines
            if the node meets some criteria.

    Returns:
        nx.Graph: Filtered network (only nodes that meet filter criteria remain).
    """
    pass


def obfuscate_locations(network: nx.Graph, max_radius: float):
    """
    Obfuscate node locations by shifting them randomly within a specified radius.

    Args:
        network (nx.Graph): The input network with location data as node attributes.
        max_radius (float): Maximum radius for random shifts.

    Returns:
        nx.Graph: The obfuscated network.
    """
    pass


def calculate_edge_lengths(network: nx.Graph):
    """
    Calculate the lengths of all edges in the network based on node locations.

    Args:
        network (nx.Graph): Network with geospatial node attributes.

    Returns:
        list: Sorted list of edge lengths.
    """
    pass


def compare_edge_length_distributions(original: list, perturbed: list, granularity=100):
    """
    Compute statistical comparisons between two edge length distributions.

    Args:
        original (list): Edge lengths from the original network.
        perturbed (list): Edge lengths from a perturbed network.

    Returns:
        tuple: KS statistic, total CDF area difference.
    """

    def proportion_under(sequence, value):
        lo = 0
        hi = len(sequence) - 1
        while lo < hi:
            mid = int((hi-lo)/2) + lo
            if sequence[mid] > value:
                hi = mid
            else:
                lo = mid + 1

        if sequence[lo] <= value:
            lo = lo + 1
        return lo / len(sequence)


    o_sorted = sorted(original)
    p_sorted = sorted(perturbed)

    n = len(o_sorted)

    x_vals = np.linspace(min(o_sorted[0], p_sorted[0]), max(o_sorted[-1],p_sorted[-1]), n*granularity)

    ks = 0
    cdf_total_diff = 0

    for x in x_vals:
        p_prob_lt_x = proportion_under(p_sorted, x)
        o_prob_lt_x = proportion_under(o_sorted, x)
        cdf_total_diff += abs(p_prob_lt_x - o_prob_lt_x)
        ks = max(ks, abs(p_prob_lt_x - o_prob_lt_x))
        print(f"{x:.2f} : {o_prob_lt_x:.2f} - {p_prob_lt_x:.2f}, ks:{p_prob_lt_x - o_prob_lt_x:.2f}, cdf:{cdf_total_diff:.2f}.")

    print(len(x_vals))
    return (ks, cdf_total_diff/(n*granularity))


def perturbation_box_whisker(original: list, perturbed: list, region_avg_diameter=None):
    """
        Generate a box and whisker plot of relative perturbation of all edge lengths.

        e.g. original = [1,1,1,2,2,3,5]
            perturbed = [1,2,0,2,1,5,7]
            relative perturbations: [0,1,1,0,1,.66,.4]
            turn that into a box and whisker plot to show the distribution.

        if region_avg_diameter is supplied, mark it on the box and whisker. That should
        give a good baseline for what would be an expected maximum for our algorithm.
    """
    pass

def run_experiment(network_path: str, region_path: str, subregion_filter=None,
                   results_name="exp_result"):
    """
    Run the full experiment pipeline, applying obfuscation and evaluating effects.
    Saves all results to:
        {results_name}_edge_perturbation.png
        {results_name}_edge_perturbation.txt
        {results_name}_network_visualization.png

    Args:
        network_path (str): Path to the network dataset.
        region_path (str): Path to the region shapefile.
        subregion_filter (optional): Criteria for filtering subregions.

    Returns:
        None
    """
    pass

def a_filter(node, regions) -> bool:
    '''
    Placeholder for a function that filters nodes.
    '''
    pass

if __name__ == '__main__':

    # experiments = [
    #     ("network_file.pkl","regions.pkl",None),
    #     ("network_file.pkl","regions.pkl",a_filter),
    # ]

    # count = 0
    # for ntwk, regions, filter in experiments:
    #     result_name = f"exp_result-{count}"
    #     run_experiment(ntwk, regions, filter, result_name)

    a = [1,1,1,4,4,4]
    b = [1,2,3,4,5,6]
    print(compare_edge_length_distributions(a,b,granularity=6))
