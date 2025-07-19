#!/usr/bin/env python3

import random
import sys

def makeProcess():
    processes = []
    inputChoice = input("Do you want a [M]ANUAL or [R]ANDOM process generation? [M/R]: ").strip().upper()
    if inputChoice == 'M':
        n = int(input("Input number of processes: "))
        for i in range(1, n + 1):
            arrival = int(input(f"  Arrival time of P{i}: "))
            burst = int(input(f"  Burst time of P{i}: "))
            processes.append({'pid': i, 'arrival': arrival, 'burst': burst})
    else:
        n = int(input("Number of processes you want to generate: "))
        maxArrival = int(input("Input integer for max arrival time: "))
        maxBurst = int(input("Input integer for max burst time: "))
        for i in range(1, n + 1):
            arrival = random.randint(0, maxArrival)
            burst = random.randint(1, maxBurst)
            processes.append({'pid': i, 'arrival': arrival, 'burst': burst})
    return processes

def sjf(processes):
    time = 0
    events = []
    stats = {}
    remaining = processes.copy()

    while remaining:
        ready = [p for p in remaining if p['arrival'] <= time]

        if ready:
            current = sorted(ready, key=lambda p: (p['burst'], p['arrival'], p['pid']))[0]
            pid, arrival, burst = current['pid'], current['arrival'], current['burst']

            if time < arrival:
                events.append((time, arrival, 'idle'))
                time = arrival

            start = time
            end = start + burst
            time = end

            stats[pid] = {
                'arrival': arrival,
                'burst': burst,
                'startTime': start,
                'completeTime': end,
                'turnaround': end - arrival,
                'response': start - arrival
            }
            events.append((start, end, f"P{pid}"))
            remaining = [p for p in remaining if p['pid'] != pid]
        else:
            nextArrival = min(p['arrival'] for p in remaining)
            events.append((time, nextArrival, 'idle'))
            time = nextArrival

    return events, stats

def printGantt(events):
    chart = ""
    times = ""
    for(startTime, end, label) in events:
        width = end - startTime

        block = "|" + label.center(width*2) 
        chart = chart + block
        lastTime = end

        chart = chart + "|"

        times = "0".rjust(2)
        for(startTime, end, _) in events:
            times = times + str(end).rjust(len(label)*2 + 1)
        print("\nGantt Chart:\n")
        print(chart)
        print(times, "\n")

def printStats(stats):
    print("Per-process metrics:")
    header = f"{'PID':>3} {'AT':>3} {'BT':>3} {'ST':>3} {'CT':>3} {'TAT':>4} {'RT':>3}"
    print(header)
    print("-" * len(header))
    totalTurnaround = totalResponse = 0
    for pid in sorted(stats):
        s = stats[pid]
        totalTurnaround += s['turnaround']
        totalResponse += s['response']
        print(f"{pid:>3} {s['arrival']:>3} {s['burst']:>3} {s['startTime']:>3} {s['completeTime']:>3} {s['turnaround']:>4} {s['response']:>3}")
    n = len(stats)
    print("\nAverages:")
    print(f"  Average Turnaround Time: {totalTurnaround / n:.2f}")
    print(f"  Average Response   Time: {totalResponse / n:.2f}")

def main():
    print("\n=== Shortest Job First (SJF) Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = sjf(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__main__":
    main()
