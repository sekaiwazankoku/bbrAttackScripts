import os
import sys
import math
import random

if (__name__ == "__main__"):

    # Link rate decreases
    rate = [8, 4, 2]

    # Link rate increases
    rate = [2, 4, 8]

    total_time = 60 * 1e3  # ms

    interval_duration = total_time / len(rate)
    rate_idx = 0
    current_time = 0
    while(current_time <= total_time):
        if (current_time > (rate_idx + 1) * interval_duration):
            rate_idx += 1
        this_rate = rate[rate_idx]
        print(f"{current_time}\n"*this_rate, end="")
        current_time += 1