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
    max_burst = rate * jitter  # pkts

    total_time = 60 * 1e3  # ms

    fname = f"rate[{rate}]-delay[{delay}]-aggregation[{jitter}].trace"

    with open(os.path.join(outdir, fname), "w") as f:
        current_time = 0  # ms
        while(current_time <= total_time):
            this_burst_size = int(random.uniform(1, max_burst+1))
            # this_burst_size = math.ceil(math.ceil(this_burst_size / rate) * rate)
            current_time += math.ceil(this_burst_size / rate)
            # print(f"{current_time}\n"*this_burst_size, end="")
            f.write(f"{current_time}\n"*this_burst_size)