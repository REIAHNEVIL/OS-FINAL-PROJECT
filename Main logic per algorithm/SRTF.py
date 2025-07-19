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

def srtf(processes):
    time = 0
    events = []
    stats = {}
    ready = []
    remaining = {p['pid']: p['burst'] for p in processes}
    arrived = []
    currentProcess = None
    lastSwitch = 0
    finished = 0
    n = len(processes)

    while finished < n:
        for p in processes:
            if p['arrival'] == time:
                arrived.append(p)

        ready += [p for p in arrived if p['pid'] not in [r['pid'] for r in ready]]
        ready = [p for p in ready if remaining[p['pid']] > 0]

        if ready:
            ready.sort(key=lambda p: (remaining[p['pid']], p['arrival'], p['pid']))
            nextProcess = ready[0]

            if currentProcess is None or currentProcess['pid'] != nextProcess['pid']:
                if currentProcess:
                    events.append((lastSwitch, time, f"P{currentProcess['pid']}"))
                currentProcess = nextProcess
                lastSwitch = time

                if 'startTime' not in stats.get(currentProcess['pid'], {}):
                    if currentProcess['pid'] not in stats:
                        stats[currentProcess['pid']] = {
                            'arrival': currentProcess['arrival'],
                            'burst': currentProcess['burst']
                        }
                    stats[currentProcess['pid']]['startTime'] = time

            remaining[currentProcess['pid']] -= 1
            time += 1

            if remaining[currentProcess['pid']] == 0:
                events.append((lastSwitch, time, f"P{currentProcess['pid']}"))
                stats[currentProcess['pid']]['completeTime'] = time
                stats[currentProcess['pid']]['turnaround'] = time - currentProcess['arrival']
                stats[currentProcess['pid']]['response'] = stats[currentProcess['pid']]['startTime'] - currentProcess['arrival']
                print(f"P{currentProcess['pid']}: ST={stats[currentProcess['pid']]['startTime']}, CT={time}, AT={currentProcess['arrival']}, RT={stats[currentProcess['pid']]['response']}, TAT={stats[currentProcess['pid']]['turnaround']}")
                finished += 1
                currentProcess = None
        else:
            time += 1

    return events, stats

def printGantt(events):
    chart = ""
    times = ""
    for(startTime, end, label) in events:
        width = end - startTime

        block = "|" + label.center(width*2) 
        chart = chart + block

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
    print("\n=== Shortest Remaining Time First (SRTF) Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = srtf(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__main__":
    main()
