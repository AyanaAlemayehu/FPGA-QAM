'''

File transmits IQ values over a socket to simulate data transmission algorithms

'''
import math
from multiprocessing.connection import Client
import time
import random
import numpy as np

# Simulation Constants/Globals
SAMPLE_RATE = 1000 #how fast time steps are incremented per second
SIM_DELTA = 1/SAMPLE_RATE #fractional amount of seconds incremented per sim step
SIM_TIME = 0 # the current time of the sim
SNR_DB = 100 #signal to noise ratio (in decibels)

# transmitter constants
CARRIER_FREQ = 100
IQ_MOD_FREQ = 5 # receiver knows this value
PHASE_DELAY = math.pi/6
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

def mix_iq(i, q, noise=False):
    # noise is calculated assuming average power of signal is 2 (ranges from -2 to 2 so power ranges from 0 to 4) (its the square of the signal)
    signal_average_db = 10*math.log10(2)
    noise_average_db = signal_average_db - SNR_DB
    noise_power = 10**(noise_average_db/10)
    noise = np.random.normal(0, np.sqrt(noise_power)) if noise else 0
    return i*math.cos(2*math.pi*CARRIER_FREQ*SIM_TIME + PHASE_DELAY) + q*math.sin(2*math.pi*CARRIER_FREQ*SIM_TIME + PHASE_DELAY) + noise

def send_qam(conn, noise=False):
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
            conn.send(mix_iq(x, y, noise=noise))
        else:
            conn.send(mix_iq(1, 1, noise=noise))
        step_time()

def send_garbage(conn):
    print("sending garbage")
    for i in range(random.randint(0,20)):
        conn.send(mix_iq(random.randint(0, 1),random.randint(0, 1)))
        step_time()

def send_packet(conn, noise=False, calibrate=False):
    if calibrate:
        # first send 4 calibrating alternating I and Q values 
        # (in this case its (0, 1) and (0, -1))
        print("sending calibration")
        start_iter = ITER
        while ITER < start_iter + 4:
            if (ITER % 2 == 0):
                conn.send(mix_iq(0, 1, noise=noise))
            else:
                conn.send(mix_iq(0, -1, noise=noise))
            step_time()
    # then after this calibration stage send packet data, in this case a QAM constellation
    # print("sending QAM")
    # send_qam(conn, noise=noise)


if __name__ == "__main__":
    print("Running sim with below specs")
    print("SNR: ", SNR_DB)
    print("PHASE DELAY: ", PHASE_DELAY, " (in degrees) ", PHASE_DELAY*57.2958, "°")
    print("----------------------------------------")

    address = ('localhost', 6000)
    conn = Client(address)
    send_garbage(conn)
    send_packet(conn, noise=True, calibrate=True)
    conn.send('close')