from dataclasses import dataclass
import pickle
import sys

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter

import geojitter as gj


@dataclass
class StateAnalytics:
    dataset: int
    state: int

    wass_rad: float
    wass_tile: float
    wass_region: float

    ks_rad: float
    ks_tile: float
    ks_region: float

    quartiles_rad: list[float]
    quartiles_tile: list[float]
    quartiles_region: list[float]


fig = plt.figure()
gs = GridSpec(2, 3, height_ratios=[1, 1])

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[1, :])

ax1.set_title("By radius")
ax2.set_title("By tile")
ax3.set_title("By county")

wasserstein_rad = gj.wasserstein(
    focused_network_tile, by_radii, ax1)
ks_rad = gj.kolmogorov_smirnov(focused_network_tile, by_radii)
between_rad = gj.analyze_betweenness_centrality(
    focused_network_tile, by_radii)

wasserstein_tile = gj.wasserstein(
    focused_network_tile, by_tile, ax2)
ks_tile = gj.kolmogorov_smirnov(focused_network_tile, by_tile)
between_tile = gj.analyze_betweenness_centrality(
    focused_network_tile, by_tile)

wasserstein_region = gj.wasserstein(
    focused_network_counties, by_region, ax3)
ks_region = gj.kolmogorov_smirnov(
    focused_network_counties, by_region)
between_region = gj.analyze_betweenness_centrality(
    focused_network_counties, by_region)

ax1.text(0.2, 0.1, f"Wass. Distance = {
         wasserstein_rad:.4f}\nKS GoF = {ks_rad:.4f}", size='xx-small')
ax2.text(0.2, 0.1, f"Wass. Distance = {wasserstein_tile:.4f}\nKS GoF = {
         ks_tile:.4f}", size='xx-small')
ax3.text(0.2, 0.1, f"Wass. Distance = {wasserstein_region:.4f}\nKS GoF = {
         ks_region:.4f}", size='xx-small')

box1 = gj.normal_signed_distance(focused_network_tile, by_radii)
box2 = gj.normal_signed_distance(focused_network_tile, by_tile)
box3 = gj.normal_signed_distance(
    focused_network_counties, by_region)

state_analytics.append(asdict(StateAnalytics(
    dataset=i,
    state=j,
    wass_rad=wasserstein_rad,
    wass_tile=wasserstein_tile,
    wass_region=wasserstein_region,
    ks_rad=ks_rad,
    ks_tile=ks_tile,
    ks_region=ks_region,
    quartiles_rad=np.percentile(
        box1, [0, 25, 50, 75, 100], method='midpoint'),
    quartiles_tile=np.percentile(
        box2, [0, 25, 50, 75, 100], method='midpoint'),
    quartiles_region=np.percentile(
        box3, [0, 25, 50, 75, 100], method='midpoint')
)))

ax4.boxplot([box1, box2, box3])
ax4.set_title("Percentage change to edge length")
ax4.set_xticklabels(["Radius", "Tile", "County"])
ax4.yaxis.set_major_formatter(
    FuncFormatter(lambda x, _: f'{x*100:.0f}%'))

if i == 1:  # Brightkite
    fig.suptitle(f"Brightkite Results: {trial_state}")
    plt.tight_layout()
    plt.savefig(f"{output_path}/bk-{trial_state}.png")
elif i == 0:
    fig.suptitle(f"Gowalla Results: {trial_state}")
    plt.tight_layout()
    plt.savefig(f"{output_path}/gw-{trial_state}.png")
plt.close()

# Graphing Betweenness Centrality
bc_tile = nx.betweenness_centrality(focused_network_tile)
bc_region = nx.betweenness_centrality(focused_network_counties)

delta_bc_rad = dictwise_subtract(bc_tile, between_rad)
delta_bc_tile = dictwise_subtract(bc_tile, between_tile)
delta_bc_region = dictwise_subtract(bc_region, between_region)

fig, axs = plt.subplots(
    3, 1, sharey=True, sharex=True, tight_layout=True)

axs[0].set_yscale("log")
axs[0].set_title("By Radius")
axs[0].hist(delta_bc_rad.values(), bins=20)

axs[1].set_yscale("log")
axs[1].set_title("By Tile")
axs[1].hist(delta_bc_tile.values(), bins=20)

axs[2].set_yscale("log")
axs[2].set_title("By Region")
axs[2].hist(delta_bc_region.values(), bins=20)

fig.suptitle(
    f"Logarithmic Histogram of Betweenness Centrality Deltas: {trial_state}")
fig.supxlabel("Delta Betweenness Centrality (20 bins)")
fig.supylabel("Log of the Frequency of Each Delta")
plt.savefig(f"{output_path}/bcd-{trial_state}.png")
plt.close()

print(trial_state, "is done!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: py analyze_trials.py <trial_folder>")
        exit(0)
