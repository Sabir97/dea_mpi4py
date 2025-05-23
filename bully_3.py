from mpi4py import MPI
# import numpy as np
import sys
import psutil


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
status = MPI.Status()

initiator = 0

class Msg:
    def __init__(self, uid, type):
        self.uid = uid
        self.type = type

init = True
found = False


start_time = MPI.Wtime()
p = psutil.Process()

stop_time = 0
msg_count = 0
min_time = 0
max_time = 0
total_msg = 0

# if init==True:
if rank == initiator:
    if init:
        msg = Msg(rank, "election")
        for hrp in range(rank+1, size):
            comm.send(msg, dest=hrp)
            msg_count += 1
            print(f"Process {rank} sent ", msg.type, f" message to process {hrp}")
            sys.stdout.flush()  # Force output

        r = comm.recv(status=status)
        print(f'{rank} received ', r.type, f' message from process {status.Get_source()}')
        sys.stdout.flush()
        init = False


    # else:
while(not found):
        r = comm.recv(source = MPI.ANY_SOURCE, status=status)
        print(f'{rank} received', r.type, f' message from process {status.Get_source()}')
        # init = False

    # else:
        # r = comm.recv(status=status)
        # print(f"Process {rank} received {r.type} message from process {status.Get_source()}")
        # sys.stdout.flush()

        s = status.Get_source()
        # r = comm.recv(source = MPI.ANY_SOURCE, status=status)
        # print(f"Process {rank} received message from process {status.Get_source()}")
        if r.type == "election" and r.uid<rank:
            msg = r
            msg.type = "OK"
            msg.uid = rank
            comm.send(msg, dest=s)
            msg_count += 1
            print(f"Process {rank} sent OK message to process {s}")
            msg = Msg(rank, "election")

            if rank == size-1:
                leader_msg = Msg(rank, "leader")
                # leader = comm.bcast(leader_msg, root = rank)
                leader = leader_msg.uid
                print(f"{rank} says i'm the leader")
                print(rank, " broadcasted a leader message to other processes")
                for lrp in range(0, rank):
                    comm.send(leader_msg, dest=lrp)
                    msg_count += 1

                found = True
                stop_time = MPI.Wtime()
               
                # sys.stdout.flush()

            else:
                for hrp in range(rank+1, size):
                    elect_msg = Msg(rank, "election")
                    comm.send(msg, dest=hrp)
                    msg_count += 1
                    print(f"Process {rank} sent Election message to process {hrp}")

            # r = comm.recv(source = MPI.ANY_SOURCE, status=status)
            # print(f"Process {rank} received ", r.type, f" message from process {status.Get_source()}")

        elif rank<r.uid:
            # r = comm.recv(status=status)
            # s = status.Get_source()
            # print(f'{rank} received', {r.type}, f' from {s}')
            if r.type =="leader":
                leader = r.uid
                found = True
                stop_time = MPI.Wtime()

                # min_time = comm.reduce(start_time,  MPI.MIN, root = initiator)
                # max_time = comm.reduce(stop_time, MPI.MAX, root=initiator)
                # total_msg = comm.reduce(msg_count, MPI.SUM, root=initiator)

min_time = comm.reduce(start_time, MPI.MIN, root=initiator)
max_time = comm.reduce(stop_time, MPI.MAX, root=initiator)
total_msg = comm.reduce(msg_count, MPI.SUM, root=initiator)

mem = p.memory_info().rss

max_mem = comm.reduce(mem, MPI.MAX, root=initiator)

if(rank == initiator):
    print(f'Election time: {max_time-min_time} seconds \n Exchanged Messages: {total_msg*2}')
    print(f'Max resident memory: {max_mem/(1024*1024)} MB')

    # sys.stdout.flush()


