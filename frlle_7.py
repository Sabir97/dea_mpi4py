from mpi4py import MPI
import sys
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
status = MPI.Status()

found = False
init = True

next_rank = (rank + 1) % size
prev_rank = (rank - 1) % size

dms = [0, 3, 5, 2, 1, 4]

class Message:
    def __init__(self, uid, val, direction, type):
        self.uid = uid
        self.val = val
        self.direction = direction
        self.type = type



leader = rank
count = 0
msg_count = 0

# Dataset 3
dataset3 = np.array([
        [12,	8,	1/500,	2,	1/17,	1/20,	1/16,	1/32,	1,	    1/13,   100,	 10],
        [37,	30,	1/3938,	19,	1/20,	1/15,	1/14,	1/10,	0.8,	1/366,	25,	    2.5],
        [44,	23,	1/4401,	13,	1/19,	1/18,	1/20,	1/22,	0.6,	1/486,	50,	      5],
        [29,	11,	1/3477,	5,	1/18,	1/9,	1/22,	1/31,	0.3,	1/198,	20,	      2],
        [38,	10,	1/5029,	3,	1/17,	1/11,	1/10,	1/19,	1,	    1/103,	500,	200],
        [24,	18,	1/1846,	9,	1/21,	1/13,	1/18,	1/28,	0.8,	1/232,	20,  	  2]
])

set3_merec_weights = np.array([0.103, 0.077, 0.08,  0.147, 0.013, 0.046, 0.032, 0.042, 0.094, 0.135, 0.103, 0.127])

    # Generate random values for CPU usage, Memory usage, Bandwidth usage, and Failure rate
# cpu_usage = np.random.uniform(10, 50, 6)  # CPU usage between 10% and 50%
# memory_usage = np.random.uniform(1, 8, 6)  # Memory usage between 1GB and 8GB
# bandwidth_usage = np.random.uniform(100, 1000, 6)  # Bandwidth usage between 100Mbps and 1000Mbps
# failure_rate = np.random.uniform(0.01, 0.1, 6)  # Failure rate between 1% and 10%

# Combine all metrics into a single array
# metrics = np.array([cpu_usage, memory_usage, bandwidth_usage, failure_rate])

# print(metrics)

generated_dataset = np.array([
    [ 19.82084662,  14.34741469,  24.35515827,  18.22981288,  15.85645532, 49.88328263], # CPU Usage
    [  6.82160718,   4.90008034,   7.44527413,   7.68725833,   4.920543, 7.54606917], # Memory Usage
    [750.73785094, 303.62774695, 837.90179859, 554.30239513, 839.72729417, 420.48178519], # Bandwidth Usage
    [0.07744207,   0.06807406,   0.02291997,   0.0504849,    0.07551011, 0.0984064 ] # Failure Rate
    ])

generated_dataset = generated_dataset.transpose()

# print(generated_dataset)

# Generate four different weights for the four metrics, ensuring they add up to one
# generated_weights = np.random.dirichlet(np.ones(4), size=1)[0]

generated_weights = np.array([0.10673913, 0.09915818, 0.0332699,  0.7608328])
# print(generated_weights)
# print('Sum of weights:', np.sum(generated_weights))


# mlc = sys.maxsize # theoritical max leader coefficient value

lc = 0

for j in range(generated_weights.shape[0]):
    lc += generated_weights[j]*generated_dataset[rank, j]

# print(generated_weights)
print(f"Leader Coefficient of {rank} is {lc}")
val = lc
mlc = lc
# val = rank

start_time = MPI.Wtime()

frem = True
ein = False

if rank == 0 and init == True:
    leader = rank
    ein = True
    msg = Message(rank, val, "clockwise", "election")
    req1 = comm.isend(msg, dest=next_rank)
    req2 = comm.isend(msg, dest=prev_rank)
    # MPI.Request.Waitall([req1, req2])
    msg_count += 2
    print(f"{rank} has initiated the election !")
    print(f'{rank} sent a message to {next_rank} and {prev_rank}')
    sys.stdout.flush()
    init = False

# Dictionary to store pending receive requests
recv_requests = {}

left_uid = []
right_uid = []

left_leader = []
right_leader = []



while not found:
    # Post non-blocking receives from both directions
    if next_rank not in recv_requests:
        recv_requests[next_rank] = comm.irecv(source=next_rank)
        emat = MPI.Wtime()
    if prev_rank not in recv_requests:
        recv_requests[prev_rank] = comm.irecv(source=prev_rank)
        emat = MPI.Wtime()

    # recv_requests[prev_rank] = comm.irecv(source=prev_rank)
    # recv_requests[next_rank] = comm.irecv(source=next_rank)
    # r = r.wait(status=status)
    
    # if status.Get_source() == prev_rank:
    #     recv_requests[prev_rank] = comm.irecv(source=prev_rank)
    # elif status.Get_source() == next_rank:
    #     recv_requests[next_rank] = comm.irecv(source=next_rank)

    # Test for completed receives
    for source in list(recv_requests.keys()):
        request = recv_requests[source]
        completed, r = request.test()
        # r = request.wait()
        
        if completed and r is not None:
            count += 1
            # print(f'count is {count}')
            del recv_requests[source]  # Remove completed request
            
            # Handling Left messages (Clockwise Direction)
            if source == prev_rank:
                print(f"Node {rank} received ID {r.uid} from node {source} from clockwise direction")
                sys.stdout.flush()
                left_uid.append(r.uid)

                if r.type == 'leader':
                    if r.uid in right_leader:
                        leader = r.uid
                        found = True
                        print(f"Process {rank} discarded leader message {leader}")
                        sys.stdout.flush()

                    else:
                        leader = r.uid
                        left_leader.append(leader)

                        found = True
                        print(f"{rank} received leader is: {leader}")
                        req = comm.isend(r, dest=next_rank)
                        # req.wait()
                        print(f'{rank} sent leader message to {next_rank}')
                        print(f"{rank} stopped running")
                        sys.stdout.flush()
                        msg_count += 2
                        # comm.Barrier()
                        # end_time = MPI.Wtime()

                        # min_time = comm.reduce(start_time, op=MPI.MIN, root=0)
                        # max_time = comm.reduce(end_time, op=MPI.MAX, root=0)
                        # nbr_msg = comm.reduce(msg_count, op=MPI.SUM, root=0)

                    # MPI.Finalize()

                elif r.type == "election":
                    if r.uid in right_uid:
                        leader = r.uid
                        found = True

                        r.type= "leader"
                        
                        
                        req1 = comm.isend(r, dest=next_rank)
                        req2 = comm.isend(r, dest=prev_rank)
                        MPI.Request.Waitall([req1, req2])
                        print(f'Process {rank} declares {leader} as leader')
                        print(f'{rank} sent a message to {next_rank} and {prev_rank}')
                        sys.stdout.flush()

                        msg_count += 2

                    elif r.val < mlc:
                        leader = r.uid
                        mlc = r.val
                        req = comm.isend(r, dest=next_rank)
                        frem = False
                        req.wait()
                        # print(f'{rank} Updated leader to {leader}')
                        print(f'{rank} sent a message to {next_rank}')
                        sys.stdout.flush()
                        msg_count += 1

                    elif r.val > mlc:
                        # leader = rank
                        # request.cancel()
                        # r.uid = rank
                        # r.val = val
                        # # msg = Message(r, val, 'clockwise', 'election')
                        # req1 = comm.isend(r, dest=next_rank)
                        # req2 = comm.isend(r, dest=prev_rank)
                        # MPI.Request.Waitall([req1, req2])
                        # print('sending my UID')
                        print(f'{rank} Discarded the message of {r.uid}')
                        sys.stdout.flush()
                        # msg_count += 2

                        if(frem == True and ein == False):
                            r.uid = rank
                            r.val = val
                            req1 = comm.isend(r, dest=next_rank)
                            req2 = comm.isend(r, dest=prev_rank)
                            frem = False
                            ein = True
                            MPI.Request.Waitall([req1, req2])
                            print(f'{rank} sent a message to {next_rank} and {prev_rank}')
                            sys.stdout.flush()
                            msg_count += 2

                    elif r.val == mlc:
                        if r.uid < rank:
                            r.uid = rank 
                            r.val = lc
                            req = comm.isend(r, dest=next_rank)
                            frem = False
                            req.wait()
                            print(f'{rank} Copied its UID to the election message')
                            print(f'{rank} sent the message to {next_rank}')
                            sys.stdout.flush()
                            msg_count += 2
                        
                        elif leader < r.uid:
                            # leader = r.uid
                            req = comm.isend(r, dest=next_rank)
                            print(f'{rank} sent the message to {next_rank}')
                            sys.stdout.flush()
                            
                        elif r.uid == leader:
                            r.type = "leader"
                            leader = r.uid
                            req1 = comm.isend(r, dest=next_rank)
                            req2 = comm.isend(r, dest=prev_rank)
                            MPI.Request.Waitall([req1, req2])
                            print(f'{rank} sent a leader message to {next_rank} and {prev_rank}')
                        else:
                            print(f'{rank} Discarded the message of {r.uid}')
                            sys.stdout.flush()

            # Right Messages (Counter Clockwise Direction)
            elif source == next_rank:
                print(f"Node {rank} received ID {r.uid} from node {source} following counter clockwise direction")
                right_uid.append(r.uid)

                if r.type == "leader": #and rank != r.uid:
                    if r.uid in left_leader:
                        leader = r.uid
                        found = True
                        print(f"Process {rank} discarded leader message {leader}")
                        sys.stdout.flush()

                    else:
                        print(f'{rank} received leader is {r.uid} from {next_rank}')
                        sys.stdout.flush()
                        
                        # if rank != r.uid:
                        found = True
                        leader = r.uid
                        right_leader.append(leader)
                        # print(f"{rank} says that new leader is: {leader}")
                        req = comm.isend(r, dest=prev_rank)
                        # req.wait()
                        print(f'{rank} sent leader message to {prev_rank}')
                        print(f"{rank} stopped running")
                        sys.stdout.flush()
                        msg_count += 2

                        # end_time = MPI.Wtime()

                        # min_time = comm.reduce(start_time, op=MPI.MIN, root=0)
                        # max_time = comm.reduce(end_time, op=MPI.MAX, root=0)
                        # nbr_msg = comm.reduce(msg_count, op=MPI.SUM, root=0)


                    # MPI.Finalize()

                elif r.type == "election":
                    if r.uid in left_uid:
                        leader = r.uid
                        found = True
                        r.type = "leader"
                        # lmsg = Message(leader, val, 'clockwise', 'leader')
                        # print(f"Process {rank} Discarded leader message")
                        sys.stdout.flush()
                        req1 = comm.isend(r, dest=next_rank)
                        req2 = comm.isend(r, dest=prev_rank)
                        MPI.Request.Waitall([req1, req2])
                        print(f'Process {rank} declares {leader} as leader')
                        print(f'{rank} sent a message to {next_rank} and {prev_rank}')
                        sys.stdout.flush()

                        msg_count += 2

                    if(r.val < mlc):
                        mlc = r.val
                        leader = r.uid
                        req = comm.isend(r, dest=prev_rank)
                        frem = False
                        req.wait()
                        # print(f'{rank} updated leader to {leader}')
                        print(f'{rank} sent a message to {prev_rank}')
                        sys.stdout.flush()
                        msg_count += 2

                    elif(mlc<r.val):
                        # leader = rank
                        # r.uid = rank
                        # r.val = val
                        # req1 = comm.isend(r, dest=next_rank)
                        # req2 = comm.isend(r, dest=prev_rank)
                        # MPI.Request.Waitall([req1, req2])
                        # request.cancel()
                        # print('Updated election message')
                        print(f'{rank} Discarded the message of {r.uid}')
                        sys.stdout.flush()

                        if(frem == True and ein == False):
                            r.uid = rank
                            r.val = val
                            req1 = comm.isend(r, dest=next_rank)
                            req2 = comm.isend(r, dest=prev_rank)
                            frem = False
                            ein = True
                            MPI.Request.Waitall([req1, req2])
                            print(f'{rank} sent a message to {next_rank} and {prev_rank}')
                            sys.stdout.flush()
                            msg_count += 2

                        # msg_count += 2

                    elif r.val == mlc:
                        if(frem == True and ein == False):
                            if rank > r.uid:
                                r.uid = rank 
                                r.val = lc
                                req = comm.isend(r, dest=prev_rank)
                                frem = False
                                req.wait()
                                print(f'{rank} Copied its UID to the election message')
                                print(f'{rank} sent the message to {prev_rank}')
                                sys.stdout.flush()
                                msg_count += 2

                            frem = False

                        elif leader < r.uid:
                            # leader = r.uid
                            req = comm.isend(r, dest=next_rank)
                            req.wait()
                            print(f'{rank} sent the message to {next_rank}')
                            sys.stdout.flush()
                            
                        elif r.uid == leader:
                            r.type = "leader"
                            leader = r.uid
                            req1 = comm.isend(r, dest=next_rank)
                            req2 = comm.isend(r, dest=prev_rank)
                            MPI.Request.Waitall([req1, req2])
                            print(f'{rank} sent a leader message to {next_rank} and {prev_rank}')
                        else:
                            print(f'{rank} Discarded the message of {r.uid}')
                            sys.stdout.flush()

# final_recv = comm.irecv()
# r = final_recv.wait()




# Cancel any pending receives
# for source in list(recv_requests.keys()):
#     request = recv_requests[source]
#     if not request.test()[0]:
#         request.cancel()
#         print(f"Rank {rank}: Cancelled pending request from {source}")
#         sys.stdout.flush()
#     del recv_requests[source]

# Final receive (non-blocking version)
# req = comm.irecv()
# r = req.wait()

end_time = MPI.Wtime()
min_time = comm.reduce(start_time, op=MPI.MIN, root=leader)
max_time = comm.reduce(end_time, op=MPI.MAX, root=leader)
nbr_msg = comm.reduce(msg_count, op=MPI.SUM, root=leader)

if(rank == leader):
    print(f'Terminating Algorithm, {rank} says that leader is {leader}')

# if(rank == leader and r.type == "leader"):
    # r.cancel()

    # print(f"Leader {rank} received its leader message back")
    # sys.stdout.flush()
    # if rank == r.uid:

    print(f"end time: {end_time} on rank {rank}")
    print(f"max time: {max_time} on other processes")
    if end_time > max_time:
        total_time = end_time - min_time
    else:
        total_time = max_time - min_time
    print(str(total_time) + " seconds.")
    print(f"Total number of sent/received messages: {nbr_msg*2}")
    sys.stdout.flush()

MPI.Finalize()
    
    # comm.Barrier()


    # if rank == 0:
    #     r = comm.irecv(source=MPI.ANY_SOURCE)
    #     end_time = MPI.Wtime()
    #     min_time = comm.reduce(start_time, op=MPI.MIN, root=0)
    #     max_time = comm.reduce(end_time, op=MPI.MAX, root=0)
    #     nbr_msg = comm.reduce(msg_count, op=MPI.SUM, root=0)
    #     total_time = max_time - min_time
    #     print(f"Leader is {leader}")
    #     print(f"Total time: {total_time} seconds")
    #     print(f"Total number of messages: {nbr_msg}")
    #     sys.stdout.flush()
    #     # MPI.Finalize()

