import matplotlib.pyplot as plt

import numpy as np

# Initialize the figure and the axis
fig, ax = plt.subplots()

# Plot the west and north distance vectors
ax.quiver(0, 0, 5, 0, angles='xy', scale_units='xy', scale=1, color='r', label='West 5 km')
ax.quiver(5, 0, 0, 2, angles='xy', scale_units='xy', scale=1, color='b', label='North 2 km')

# Plot the displacement vector
ax.quiver(0, 0, 5, 2, angles='xy', scale_units='xy', scale=1, color='g', label='Displacement 5.4 km')

# Set the limits of the plot
ax.set_xlim([0, 6])
ax.set_ylim([0, 3])

# Set the aspect of the plot to be equal
ax.set_aspect('equal')

# Add a legend
plt.legend()

# Save the figure as a png file
plt.savefig('vector_diagram.png')

# Show the plot
plt.show()
