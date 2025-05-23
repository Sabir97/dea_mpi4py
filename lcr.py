from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
status = MPI.Status()

next_rank = (rank + 1) % size
prev_rank = (rank - 1) % size

order = [0, 3, 5, 2, 1, 4]

found = False
init = True

# start_time = 0
end_time = 0
msg_count = 0
min_time = 0
max_time = 0
        
start_time = MPI.Wtime()

if(rank == 0):
    if(init == True):
        # start_time = MPI.Wtime()
        leader = rank
        comm.send(rank, dest=next_rank)
        msg_count += 1
        print(f"{rank} has initiated the election !")
        sys.stdout.flush()
        init = False

while (found == False):

    incoming_rank = comm.recv(source=prev_rank, status=status)
    # Receive rank from previous process

    if(status.Get_tag() == 1 and rank != incoming_rank):
        # Leader was found and announce the new leader
        found = True
        leader = incoming_rank
        print(f"{rank} says that new leader is: {leader}")
        sys.stdout.flush()
        comm.send(leader, dest=next_rank, tag=1)
        msg_count += 1
        end_time = MPI.Wtime()
    else:
        if incoming_rank == rank:
            # Election is over, announce the leader
            leader = rank
            found = True
            print(f"Process {rank} says I'm the new leader !")
            sys.stdout.flush()
            comm.send(leader, dest= next_rank, tag=1)
            msg_count += 1
            # break
            # comm.bcast(leader, root=rank)
            
        elif incoming_rank > rank:
            # Update leader
            leader = incoming_rank
            comm.send(incoming_rank, dest=next_rank)
            msg_count += 1

        # Forward the received rank
        elif incoming_rank < rank:
            comm.send(rank, dest=next_rank)
            msg_count+= 1    

min_time = comm.reduce(start_time, op=MPI.MIN, root=5)
max_time = comm.reduce(end_time, op=MPI.MAX, root=5)

nbr_msg = comm.reduce(msg_count, op=MPI.SUM, root=5)


if(rank == 5):
    incoming_rank = comm.recv(source=prev_rank, status=status)
    if(status.Get_tag() == 1):
        end_time = MPI.Wtime()
        print(f"end time: {end_time} on rank {rank}")
        print(f"max time: {max_time} on other processes")
        # sys.stdout.flush() 
        if(end_time>max_time):
            total_time = end_time - min_time
        else:
            total_time = max_time - min_time
        # print(f"{rank} says that found = {found}") # Only 5 has changed found to true because found is local
        print(str(total_time) + " seconds.")
        print(f"Total number of sent/received messages: {nbr_msg*2}")
        sys.stdout.flush()

