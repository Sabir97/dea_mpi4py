import numpy as np

node_degree = np.array([2, 1, 2, 1, 2, 2])

n = 6

avg_centrality = np.sum(node_degree)/n # 1.66

dev = np.zeros(n)

for i in range(0,n):
    dev[i] = abs(node_degree[i] - avg_centrality)

print(avg_centrality)

print(f'Deviations: {dev}')

