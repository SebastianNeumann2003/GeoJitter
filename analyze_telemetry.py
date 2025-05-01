from scipy.stats import linregress
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt

trials = pd.read_pickle("./trial_outputs/30Apr2025 - 092810/analytics.pkl")
states = pd.read_pickle("./trial_outputs/30Apr2025 - 092810/state_analytics.pkl")

all_states = gp.read_file("./data_vault/cb_2023_us_state_20m/cb_2023_us_state_20m.shp").get(['NAME'])
print(all_states.head(50))

# Set up the figure
plt.figure(figsize=(10, 6))

techniques = ['rad', 'tile', 'region']
gowalla = states[states['dataset'] == 0]
brightkite = states[states['dataset'] == 1]

# print("Best in gowalla")
# print(gowalla.nlargest(5, 'wass_region'))
# print("Best in brightkite")
# print(brightkite.nlargest(5, 'wass_region'))

# Assign each technique a color
colors = {
    'rad': 'red',
    'tile': 'green',
    'region': 'blue'
}
pretty = {
    'rad': 'Radius',
    'tile': 'Tile',
    'region': 'Region'
}

# Plot each technique's data
for tech in techniques:
    plt.scatter(
        states[f'wass_{tech}'],
        states[f'ks_{tech}'],
        color=colors[tech],
        label=pretty[tech],
        alpha=0.7
    )

    # Extract x and y values
    x = states[f'wass_{tech}']
    y = states[f'ks_{tech}']

    # Fit linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    # Line of best fit
    line = slope * x + intercept
    plt.plot(x, line, ':', color=colors[tech], label=f'Fit: y = {slope:.3f}x + {intercept:.3f}')

    print(f"R-squared: {r_value**2:.4f}")
    print(f"P-value: {p_value:.4e}")

# Labeling and display
plt.xlabel('Wasserstein Distance')
plt.ylabel('KS Distance')
plt.title('Wasserstein vs KS Distance by Technique')
plt.legend(title='Technique')
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
for tech in techniques:
    plt.scatter(
        gowalla['state'],                # x-axis
        gowalla[f'wass_{tech}'],         # y-axis
        label=pretty[tech],
        color=colors[tech],
        marker='o',
        alpha=0.8
    )

plt.xlabel('State')
plt.ylabel('Wasserstein Distance')
plt.title('Wasserstein Distance by State')
plt.legend(title='Technique')
plt.grid(True)
plt.tight_layout()
plt.show()

# Second plot: KS distances vs state
plt.figure(figsize=(10, 6))
for tech in techniques:
    plt.scatter(
        gowalla['state'],
        gowalla[f'ks_{tech}'],
        label=pretty[tech],
        color=colors[tech],
        marker='s',
        alpha=0.8
    )

plt.xlabel('State')
plt.ylabel('KS Distance')
plt.title('KS Distance by State')
plt.legend(title='Technique')
plt.grid(True)
plt.tight_layout()
plt.show()
