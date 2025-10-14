from geopandas import GeoDataFrame, GeoSeries, read_file
from shapely import Point, Polygon
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
import numpy as np

import scipy.stats as stat
from scipy.ndimage import gaussian_filter

import geojitter as gj

# Reading
regions: GeoDataFrame = read_file(
    "./data_vault/Boston_Neighborhood_Boundaries.shp")
regions.to_crs("EPSG:4326")

# Parsing
chosen_region: Polygon = regions.iat[8, 7]
quick_ref = dict(zip(regions['name'], regions['geometry']))


def _collate(points: list[Point]):
    """
    Utility function that takes a list of Shapely Points and makes them two lists of xs and ys.
    Don't try to use this for anything other than that, it's not made to fail gracefully.
    """
    xs = []
    ys = []

    for point in points:
        xs.append(point.x)
        ys.append(point.y)

    return (xs, ys)


# I've "isolated" this into a function in case someone would want to call it multiple times
# or would want to do timing analysis on it.
# In reality it has a lot of side effects so it's not really isolated
def generate_confirmation_chart():
    xmin, ymin, xmax, ymax = chosen_region.bounds
    midx = (xmin + xmax)/2
    midy = (ymin + ymax)/2

    uniform_points = []
    gaussian_points = []
    power_points = []

    uniform_gen = gj.rand_point_in_region(
        distribution=stat.uniform,
        cache_location="uniform_gen.pkl",
        max_iter=1000,
        loc=(xmin, ymin),
        scale=((xmax-xmin), (ymax-ymin))
    )
    gaussian_gen = gj.rand_point_in_region(
        distribution=stat.multivariate_normal,
        cache_location="gaussian_gen.pkl",
        max_iter=1000,
        mean=(midx, midy),
        cov=(((xmax-xmin)/1000, 0), (0, (ymax-ymin)/1000))
    )
    power_gen = gj.rand_point_in_region(
        distribution=stat.powerlaw,
        cache_location="power_gen.pkl",
        max_iter=1000,
        loc=(xmin, ymin),
        a=0.8
    )

    for _ in range(1000):
        if (new_up := uniform_gen(Point(0, 0), chosen_region)) is not None:
            uniform_points.append(new_up)
        if (new_np := gaussian_gen(Point(0, 0), chosen_region)) is not None:
            gaussian_points.append(new_np)
        if (new_pp := power_gen(Point(0, 0), chosen_region)) is not None:
            power_points.append(new_pp)

    fig = plt.figure()
    gs = GridSpec(2, 4)

    uniform_dist_ax = fig.add_subplot(gs[0, 0])
    gaussian_dist_ax = fig.add_subplot(gs[0, 1])
    power_dist_ax = fig.add_subplot(gs[0, 2])

    uniform_actual_ax = fig.add_subplot(gs[1, 0])
    gaussian_actual_ax = fig.add_subplot(gs[1, 1])
    power_actual_ax = fig.add_subplot(gs[1, 2])

    uniform_dist_ax.set_title("(a)", loc="left")
    gaussian_dist_ax.set_title("(b)", loc="left")
    power_dist_ax.set_title("(c)", loc="left")

    fig.patch.set_facecolor('white')

    uniform_Z, xedges, yedges = np.histogram2d(
        *_collate(uniform_points),
        bins=200,
        density=False,
        range=[[xmin, xmax], [ymin, ymax]]
    )

    uniform_Z = gaussian_filter(uniform_Z, sigma=2)
    uX, uY = np.meshgrid(xedges, yedges)

    # Compute bin centers instead of edges
    xcenters = 0.5 * (xedges[:-1] + xedges[1:])
    ycenters = 0.5 * (yedges[:-1] + yedges[1:])

    CX, CY = np.meshgrid(xcenters, ycenters, indexing='xy')

    # Build mask on centers
    mask = np.array(
        [[chosen_region.contains(Point(px, py))
            for px, py in zip(x_row, y_row)]
            for x_row, y_row in zip(CX, CY)]
    )

    uniform_actual_ax.pcolormesh(uX, uY, uniform_Z.T, cmap="managua")

    gaussian_Z, xedges, yedges = np.histogram2d(
        *_collate(gaussian_points),
        bins=200,
        density=False,
        range=[[xmin, xmax], [ymin, ymax]]
    )
    # The gaussian_filter blurs, not to be confused with the
    # gaussian distribution used to choose the points
    gaussian_Z = gaussian_filter(gaussian_Z, sigma=2)
    gaussian_actual_ax.pcolormesh(CX, CY, gaussian_Z.T, cmap="managua")

    power_Z, xedges, yedges = np.histogram2d(
        *_collate(power_points),
        bins=200,
        density=False,
        range=[[xmin, xmax], [ymin, ymax]]
    )
    power_Z = gaussian_filter(power_Z, sigma=2)
    power_actual_ax.pcolormesh(CX, CY, power_Z.T, cmap="managua")

    positions = np.dstack((CX, CY))

    uniform_x = stat.uniform(loc=xmin, scale=xmax - xmin)
    uniform_y = stat.uniform(loc=ymin, scale=ymax - ymin)
    uniform_pdf = uniform_x.pdf(CX) * uniform_y.pdf(CY)

    gaussian_xy = stat.multivariate_normal(
        mean=(midx, midy),
        cov=(((xmax-xmin)/1000, 0), (0, (ymax-ymin)/1000)))
    gaussian_pdf = gaussian_xy.pdf(positions)

    power_x = stat.powerlaw(a=0.8, loc=xmin)
    power_y = stat.powerlaw(a=0.8, loc=ymin)
    power_pdf = power_x.pdf(CX) * power_y.pdf(CY)

    uniform_pdf_masked = np.where(mask, uniform_pdf, np.nan)
    gaussian_pdf_masked = np.where(mask, gaussian_pdf, np.nan)
    power_pdf_masked = np.where(mask, power_pdf, np.nan)
    cmap = plt.cm.managua.copy()
    cmap.set_bad(color='white')

    uniform_dist_ax.imshow(
        uniform_pdf_masked,
        extent=(xmin, xmax, ymin, ymax),
        origin='lower', cmap=cmap
    )
    gaussian_dist_ax.imshow(
        gaussian_pdf_masked,
        extent=(xmin, xmax, ymin, ymax),
        origin='lower', cmap=cmap
    )
    power_dist_ax.imshow(
        power_pdf_masked,
        extent=(xmin, xmax, ymin, ymax),
        origin='lower', cmap=cmap
    )

    uniform_dist_ax.set_xticks([])
    uniform_dist_ax.set_yticks([])
    gaussian_dist_ax.set_xticks([])
    gaussian_dist_ax.set_yticks([])
    power_dist_ax.set_xticks([])
    power_dist_ax.set_yticks([])
    uniform_actual_ax.set_xticks([])
    uniform_actual_ax.set_yticks([])
    gaussian_actual_ax.set_xticks([])
    gaussian_actual_ax.set_yticks([])
    power_actual_ax.set_xticks([])
    power_actual_ax.set_yticks([])

    region_gs: GeoSeries = GeoSeries(chosen_region.boundary, crs="EPSG:4326")

    region_gs.plot(ax=uniform_dist_ax, edgecolor="black", linewidth=1)
    region_gs.plot(ax=gaussian_dist_ax, edgecolor="black", linewidth=1)
    region_gs.plot(ax=power_dist_ax, edgecolor="black", linewidth=1)
    region_gs.plot(ax=uniform_actual_ax, edgecolor="black", linewidth=1)
    region_gs.plot(ax=gaussian_actual_ax, edgecolor="black", linewidth=1)
    region_gs.plot(ax=power_actual_ax, edgecolor="black", linewidth=1)

    bounds = [0, 0.33, 0.67, 1.0]
    labels = ['Low', 'Medium', 'High']

    cmap = plt.cm.managua
    handles = [
        mpatches.Patch(color=cmap(b), label=lab)
        for b, lab in zip(bounds, labels)
    ]

    leg = fig.add_subplot(gs[0, 3])
    leg.axis("off")
    leg.legend(handles=handles, title="Density", loc="center")

    # plt.show()
    plt.savefig(
        "single_neighborhood.eps",
        facecolor='white',
        transparent=False, format="eps"
    )
    plt.savefig(
        "single_neighborhood.jpg",
        format="jpg"
    )


if __name__ == "__main__":
    generate_confirmation_chart()
