import math


def smooth(f, start_time, pkts_per_ms, end_time):
    assert pkts_per_ms == math.floor(pkts_per_ms)
    assert start_time == math.floor(start_time)
    assert end_time == math.floor(end_time)

    inter_send_time = 1 / pkts_per_ms
    cur_time = start_time + inter_send_time
    while (cur_time <= end_time):
        floor_cur_time = math.floor(cur_time)
        f.write(f"{floor_cur_time}\n")
        cur_time += inter_send_time


def burst(f, start_time, wait_time, burst_size, pace_time):
    pkts_per_ms = burst_size / pace_time
    smooth(f, start_time + wait_time, pkts_per_ms,
           start_time + wait_time + pace_time)
