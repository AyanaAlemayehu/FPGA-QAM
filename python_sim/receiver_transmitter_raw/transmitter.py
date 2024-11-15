'''

File transmits IQ values over a socket to simulate different effects (phase delay, carrier freq and IQ modulation freq relationship)

'''
import math
from multiprocessing.connection import Client
import time

# Simulation Constants/Globals
SAMPLE_RATE = 1000 #how fast time steps are incremented per second
SIM_DELTA = 1/SAMPLE_RATE #fractional amount of seconds incremented per sim step
SIM_TIME = 0 # the current time of the sim

# transmitter constants
CARRIER_FREQ = 100
IQ_MOD_FREQ = 5 #receiver will need to figure this out through calibration to sample values at the right time
PHASE_DELAY = math.pi/4 # 45degree rotation to model out of sync carrier waves
ITER = 0
COUNTER = 0
QAM = 2

# utility functions
def step_time():
    global SIM_TIME, SIM_DELTA, ITER, COUNTER
    SIM_TIME += SIM_DELTA
    COUNTER += 1
    if (COUNTER == SAMPLE_RATE//IQ_MOD_FREQ):
        print("iter")
        ITER += 1
        COUNTER = 0
    time.sleep(.01)

def mix_iq(i, q):
    return i*math.cos(2*math.pi*CARRIER_FREQ*SIM_TIME + PHASE_DELAY) + q*math.sin(2*math.pi*CARRIER_FREQ*SIM_TIME + PHASE_DELAY)

def send_qam(conn):
    start_iter = ITER
    seen = set()
    while ITER - start_iter < QAM**2 + 2:
        # given I is the index of the constellation
        # x := (i % QAM)*(2/(QAM - 1)) - 1
        # y := (i // QAM)*(2/(QAM - 1)) - 1
        i = (ITER - start_iter)
        if (i < QAM**2):
            x = (i % QAM)*(2/(QAM - 1)) - 1
            y = (i // QAM)*(2/(QAM - 1)) - 1
            if ((x, y) not in seen):
                print("sending", x, y)
                seen.add((x, y))
            conn.send(mix_iq(x, y))
        else:
            conn.send(mix_iq(1, 1))
        step_time()

address = ('localhost', 6000)
conn = Client(address)
send_qam(conn)
conn.send('close')
