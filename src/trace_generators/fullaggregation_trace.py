import os
import sys
import random

from util import burst, smooth


if (__name__ == "__main__"):
    random.seed(42)

    rate = int(sys.argv[1])
    delay = int(sys.argv[2])
    outdir = sys.argv[3]

    # delay = 1  # ms
    # rate = 1  # pkt per ms

    rtprop = 2 * delay  # ms
    max_jitter = rtprop
    max_burst = rate * (max_jitter + rtprop)  # pkts

    def min_wait_time(burst_size):
        return (burst_size / rate) - rtprop

    total_time = 60 * 1e3  # ms

    fname = f"rate[{rate}]-delay[{delay}]-fullaggregation[{delay}].trace"

    with open(os.path.join(outdir, fname), "w") as f:
        current_time = 0  # ms

        smooth(f, current_time, rate, 2 * rtprop)
        current_time += 2 * rtprop

        while(current_time <= total_time):
            # Choose
            this_burst_size = max_burst
            wait_time = min_wait_time(this_burst_size)

            # Clamp
            this_burst_size = min(this_burst_size, max_burst)
            wait_time = max(wait_time, min_wait_time(this_burst_size))
            assert wait_time <= max_jitter
            pace_time = rtprop

            burst(f, current_time, wait_time, this_burst_size, pace_time)
            current_time = current_time + wait_time + pace_time
