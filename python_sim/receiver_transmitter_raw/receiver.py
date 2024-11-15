from multiprocessing.connection import Listener
from scipy.signal import kaiserord, lfilter, firwin, freqz
import math
import cmath
import matplotlib.pyplot as plt

# Simulation Constants/Globals
SAMPLE_RATE = 1000 #how fast time steps are incremented per second, akin to the ADC/DAC sample rate
SIM_DELTA = 1/SAMPLE_RATE #fractional amount of seconds incremented per sim step
SIM_TIME = 0 # the current time of the sim

# transmitter constants
CARRIER_FREQ = 100

# utility functions
def step_time():
    global SIM_TIME, SIM_DELTA
    SIM_TIME += SIM_DELTA

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

address = ('localhost', 6000)
listener = Listener(address)
conn = listener.accept()
samples = []
count = 0

while True:
    msg = conn.recv()
    if (msg != 'close'):
        samples.append(msg)
    count += 1
    if msg == 'close':
        conn.close()
        break

# with this subset of messages, determine the information modulation rate and display the QAM constellation
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
x_axis = [i for i in range(len(recovered))]
i_recovered = [i[0] for i in recovered]
q_recovered = [i[1] for i in recovered]

# print(list(zip(i_recovered, q_recovered)))

plt.scatter(i_recovered, q_recovered)
plt.grid()
# fig, ax = plt.subplots()

# ax.plot(x_axis, i_recovered, label="I")
# ax.plot(x_axis, q_recovered, label="Q")
# ax.legend()
plt.show()
print("recovered iq\n", )