import os
import sys
import math
import random


last_choice_time = 0
last_jitter_choice = 0


def get_this_delay(current_time, jitter):
    global last_jitter_choice
    global last_choice_time

    if(current_time - last_choice_time > 2 * jitter):
        this_delay = random.choice([0, jitter])
        last_jitter_choice = this_delay
        last_choice_time = current_time

    return last_jitter_choice


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

    fname = f"rate[{rate}]-delay[{delay}]-bimodal_jitter[{jitter}].trace"

    with open(os.path.join(outdir, fname), "w") as f:
        current_time = 0  # ms
        last_pkt_time = 0  # ms
        while(current_time <= total_time):
            this_delay = get_this_delay(current_time, jitter)
            this_clamped_delay = max(current_time + this_delay, last_pkt_time)
            f.write(f"{int(this_clamped_delay)}\n")
            last_pkt_time = this_clamped_delay
            current_time += 1/rate
