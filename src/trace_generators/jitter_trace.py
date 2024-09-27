import os
import sys
import math
import random

if (__name__ == "__main__"):
    random.seed(42)

    rate = int(sys.argv[1])
    delay = int(sys.argv[2])
    outdir = sys.argv[3]

    # delay = 1  # ms
    # rate = 1  # pkt per ms

    rtprop = 2 * delay  # ms
    jitter = int(rtprop / 2)

    total_time = 60 * 1e3  # ms

    fname = f"rate[{rate}]-delay[{delay}]-jitter[{jitter}].trace"

    with open(os.path.join(outdir, fname), "w") as f:
        current_time = 0  # ms
        last_pkt_time = 0  # ms
        while(current_time <= total_time):
            this_delay = int(random.uniform(0, jitter+1))
            this_clamped_delay = max(current_time + this_delay, last_pkt_time)
            f.write(f"{int(this_clamped_delay)}\n")
            last_pkt_time = this_clamped_delay
            current_time += 1/rate