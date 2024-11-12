'''
This file goes over the bare minimum to encode and decode I and Q values, and plots the output.
'''

import math
from multiprocessing.connection import Client
from scipy.signal import kaiserord, lfilter, firwin, freqz
import cmath
import matplotlib.pyplot as plt

# Simulation Constants/Globals
SAMPLE_RATE = 1000 #how fast time steps are incremented per second, akin to the ADC/DAC sample rate
NUM_SAMPLES = 4*SAMPLE_RATE
SIM_DELTA = 1/SAMPLE_RATE #fractional amount of seconds incremented per sim step
SIM_TIME = 0 # the current time of the sim

# transmitter constants
CARRIER_FREQ = 10
MOD_COUNTER = 0
MOD_MAX = NUM_SAMPLES/2 #halfway through the number of samples, the IQ values should flip
MOD_FLIP = False

# utility functions
def step_time():
    global SIM_TIME, SIM_DELTA, MOD_COUNTER, MOD_MAX, MOD_FLIP
    SIM_TIME += SIM_DELTA
    MOD_COUNTER = (MOD_COUNTER + 1) % MOD_MAX
    if (MOD_COUNTER == 0):
        MOD_FLIP = not MOD_FLIP

def mix_iq(i, q):
    return i*math.cos(2*math.pi*CARRIER_FREQ*SIM_TIME) + q*math.sin(2*math.pi*CARRIER_FREQ*SIM_TIME)

def demix_iq(signal):
    # returns in i, q format
    return (signal*math.cos(2*math.pi*CARRIER_FREQ*SIM_TIME), signal*math.sin(2*math.pi*CARRIER_FREQ*SIM_TIME))

def lowpass_filter(signal):
    # this was derived here https://scipy-cookbook.readthedocs.io/items/FIRFilter.html
    
    # The Nyquist rate of the signal.
    nyq_rate = SAMPLE_RATE / 2.0

    # The desired width of the transition from pass to stop,
    # relative to the Nyquist rate.  We'll design the filter
    # with a 5 Hz transition width.
    width = 5.0/nyq_rate

    # The desired attenuation in the stop band, in dB.
    ripple_db = 60.0

    # Compute the order and Kaiser parameter for the FIR filter.
    N, beta = kaiserord(ripple_db, width)

    # The cutoff frequency of the filter.
    cutoff_hz = 10.0 #maybe exactly the carrier frequency works?

    # Use firwin with a Kaiser window to create a lowpass FIR filter.
    taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    return lfilter(taps, 1.0, signal)

def recover_iq(ilist, qlist):
    iq_recovered = []
    for i, q in zip(ilist, qlist):
        mag = 2*((i**2 + q**2)**.5)
        ang = math.atan2(q, i)
        comp = mag*cmath.exp(1j*ang)
        iq_recovered.append((comp.real, comp.imag))
    return iq_recovered
'''

SIGNAL CREATION

'''

# signal is created by mixing iq in some predetermined sequence (right now it is alternating between (1,-1) and (-1, 1))
samples = []
for i in range(NUM_SAMPLES):
    if MOD_FLIP:
        samples.append(mix_iq(1, -1))
    else:
        samples.append(mix_iq(-1, 1))
    step_time()

'''

SIGNAL RECOVERY

'''
# signal is first recovered by again mixing i and q with cos and sin respectivley. These resulting samples will have high frequency components that 
# need to be lowpassed
i_raw = []
q_raw = []
for s in samples:
    iq = demix_iq(s)
    i_raw.append(iq[0])
    q_raw.append(iq[1])
    step_time()

# lowpass the high frequency components so that we are left with sinusoids that vary based upon information-carrying coefficients (amplitude and phase specifically)
filtered_i = lowpass_filter(i_raw)
filtered_q = lowpass_filter(q_raw)

# recover i and q now and plot (should see the alternating (1, -1) and (-1 ,1) pattern for i and q respectivley)
recovered = recover_iq(filtered_i, filtered_q)
x_axis = [i for i in range(NUM_SAMPLES)]
i_recovered = [i[0] for i in recovered]
q_recovered = [i[1] for i in recovered]

fig, ax = plt.subplots()

ax.plot(x_axis, i_recovered, label="I")
ax.plot(x_axis, q_recovered, label="Q")
ax.legend()
plt.show()
print("recovered iq\n", )




