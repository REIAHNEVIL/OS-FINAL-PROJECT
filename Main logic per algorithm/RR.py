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

def roundRobin(processes):
    try:
        quantum = int(input("Enter time quantum (default: 1): ") or 1)
    except ValueError:
        quantum = 1
        print("Invalid input. Using default time quantum = 1.")

    time = 0
    events = []
    stats = {}
    queue = []
    remaining = {p['pid']: p['burst'] for p in processes}
    arrived = []
    finished = 0
    n = len(processes)

    while finished < n:
        for p in processes:
            if p['arrival'] == time:
                arrived.append(p)

        for p in arrived:
            if p['pid'] not in [q['pid'] for q in queue] and remaining[p['pid']] > 0:
                queue.append(p)

        if not queue:
            time = time + 1
            continue

        current = queue.pop(0)
        pid = current['pid']
        arrival = current['arrival']
        burstLeft = remaining[pid]

        if pid not in stats:
            stats[pid] = {
                'arrival': arrival,
                'burst': current['burst'],
                'startTime': time
            }

        execTime = min(quantum, burstLeft)
        events.append((time, time + execTime, f"P{pid}"))
        time = time + execTime
        remaining[pid] = remaining[pid] - execTime

        for p in processes:
            if time - execTime < p['arrival'] <= time:
                arrived.append(p)
                if p['pid'] not in [q['pid'] for q in queue] and remaining[p['pid']] > 0:
                    queue.append(p)

        if remaining[pid] > 0:
            queue.append(current)
        else:
            stats[pid]['completeTime'] = time
            stats[pid]['turnaround'] = time - arrival
            stats[pid]['response'] = stats[pid]['startTime'] - arrival
            print(f"\nProcess P{pid} finished:")
            print(f"  Arrival Time   : {arrival}")
            print(f"  Burst Time     : {current['burst']}")
            print(f"  Start Time     : {stats[pid]['startTime']}")
            print(f"  Completion Time: {time}")
            print(f"  Turnaround Time: {stats[pid]['turnaround']}")
            print(f"  Response Time  : {stats[pid]['response']}\n")
            finished += 1

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
    totalWaiting = 0
    totalTurnaround = totalResponse = 0
    for pid in sorted(stats):
        s = stats[pid]
        totalTurnaround += s['turnaround']
        totalResponse += s['response']
        waiting = s['turnaround'] - s['burst']
        totalWaiting += waiting
        print(f"{pid:>3} {s['arrival']:>3} {s['burst']:>3} {s['startTime']:>3} {s['completeTime']:>3} {s['turnaround']:>4} {s['response']:>3}")
    n = len(stats)
    print("\nAverages:")
    print(f"  Average Turnaround Time: {totalTurnaround / n:.2f}")
    print(f"  Average Response   Time: {totalResponse / n:.2f}")
    print(f"  Average Waiting     Time: {totalWaiting / n:.2f}")

def main():
    print("\n=== Round Robin Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = roundRobin(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__main__":
    main()
