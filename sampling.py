import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

fig, ax = plt.subplots()


x = np.random.randint(240,size=4)
y = np.random.randint(1,high=6,size=4)
ax.scatter(x, y, c='blue', s=40, label='speedsign',alpha=0.3, edgecolors='none')

x = np.random.randint(240,size=8)
y = np.random.randint(1,high=6,size=8)
ax.scatter(x, y, c='red', s=40, label='person',alpha=0.3, edgecolors='none')

x = np.random.randint(240,size=2)
y = np.random.randint(1,high=6,size=2)
ax.scatter(x, y, c='green', s=40, label='stopsign',alpha=0.3, edgecolors='none')

x = np.random.randint(240,size=3)
y = np.random.randint(1,high=6,size=3)
ax.scatter(x, y, c='black', s=40, label='trafficlight',alpha=0.3, edgecolors='none')


ax.legend(loc = "upper right")
ax.grid(True)
ax.set_xlabel('Time (Seconds)')
ax.set_ylabel('Number Of Objects Detected')
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

plt.show()