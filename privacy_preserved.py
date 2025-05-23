import numpy as np

# votes = np.array([
#     [3, 5],  # Process 1 votes
#     [6, 1],  # Process 2 votes
#     [4, 2],  # Process 3 votes
#     [5, 6],  # Process 4 votes
#     [1, 4],  # Process 5 votes
#     [4, 3]   # Process 6 votes
# ])

# print(votes)

def tie_break():
    pass


votes = np.array([
    [2, 4],  # Process 0 votes (was Process 1)
    [5, 0],  # Process 1 votes (was Process 2)
    [3, 1],  # Process 2 votes (was Process 3)
    [4, 5],  # Process 3 votes (was Process 4)
    [0, 3],  # Process 4 votes (was Process 5)
    [3, 2]   # Process 5 votes (was Process 6)
])

num_processes = votes.shape[0]
primary_votes = np.zeros(num_processes, dtype=int)
secondary_votes = np.zeros(num_processes, dtype=int)

for i in range(num_processes):
    primary_votes[votes[i, 0]] += 1
    secondary_votes[votes[i, 1]] += 1

print(primary_votes)
print(secondary_votes)

leader = np.argmax(primary_votes)
eliminated = np.argmin(primary_votes)

primary_votes = np.delete(primary_votes, eliminated)

print(primary_votes)


