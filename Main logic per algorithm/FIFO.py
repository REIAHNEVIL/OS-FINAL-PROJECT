#!/usr/bin/env python3

import random
import sys

def makeProcess():
    processes = []
    inputChoice = input("Do you want a [M]ANUAL or [R]ANDOM process generation? [M/R]: ").strip().upper()
    if inputChoice == 'M':
        n = int(input("Input number of processes: "))
        for i in range(1, n+1):
            arrival = int(input(f"  Arrival time of P{i}: "))
            burst = int(input(f"  Burst time of P{i}: "))
            processes.append({'pid': i, 'arrival': arrival, 'burst': burst})
    else:
        n = int(input("Number of processes you want to generate: "))
        maxArrival = int(input("Input integer for max arrival time: "))
        maxBurst = int(input("Input integer for max burst time: "))
        for i in range(1, n+1):
                arrival = random.randint(0,maxArrival)
                burst = random.randint(0,maxBurst)
                processes.append({'pid':i, 'arrival': arrival, 'burst': burst})
    return processes

def fifo(processes):
    processes = sorted(processes, key=lambda p: (p['arrival'], p['pid']))
    current = 0
    events = []
    stats = {}
    for p in processes:
        pid, arrival, burst = p['pid'], p['arrival'], p['burst']

        if current < arrival:
            events.append((current, arrival, 'idle'))
            current = arrival

        startTime = current
        completeTime = startTime + burst
        turnaroundTime = completeTime - arrival
        responseTime = startTime - arrival

        stats[pid] = {
                'arrival': arrival,
                'burst': burst,
                'startTime': startTime, 
                'completeTime': completeTime,
                'turnaround': turnaroundTime, 
                'response': responseTime
        }

        events.append((startTime, completeTime, f"P{pid}"))
        current = completeTime
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
    n = len(stats)
    for pid in sorted(stats):
        tempStat = stats[pid]
        totalTurnaround += tempStat['turnaround']
        totalResponse  += tempStat['response']
        print(f"{pid:>3} {tempStat['arrival']:>3} {tempStat['burst']:>3} {tempStat['startTime']:>3} {tempStat['completeTime']:>3} {tempStat['turnaround']:>4} {tempStat['response']:>3}")
    averageTurnaround = totalTurnaround / n
    averageResponse  = totalResponse / n
    print("\nAverages:")
    print(f"  Average Turnaround Time: {averageTurnaround:.2f}")
    print(f"  Average Response   Time: {averageResponse:.2f}")

def main():
    print("\n=== FIFO Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = fifo(processes)

    printGantt(events)
    printStats(stats)

if __name__ == "__main__":
    main()
