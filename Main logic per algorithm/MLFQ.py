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


def mlfq(processes):
    try:
        totalQueues = int(input("Enter the number of queues (minimum 4): "))
        if totalQueues < 4:
            print("Number of queues must be at least 4. Setting to default (4).")
            totalQueues = 4
    except ValueError:
        print("Invalid input. Setting number of queues to default (4).")
        totalQueues = 4

    try:
        unifiedQuantum = int(input("Enter TIME QUANTUM for all queues (default 1): ") or 1)
        unifiedAllotment = int(input("Enter TIME ALLOTMENT for all queues (default 1): ") or 1)
    except ValueError:
        print("Invalid input. Using default values (1).")
        unifiedQuantum = unifiedAllotment = 1

    queueQuantum = [unifiedQuantum] * totalQueues
    allotments = [unifiedAllotment] * totalQueues

    processes.sort(key=lambda p: p['arrival'])
    origBurst = {p['pid']: p['burst'] for p in processes}
    arrivalIndex = 0
    allotmentUsed = {p['pid']: 0 for p in processes}
    time = 0
    events = []
    stats = {}
    queues = [[] for _ in range(totalQueues)]
    remaining = {p['pid']: p['burst'] for p in processes}
    service = {p['pid']: 0 for p in processes}
    processMap = {p['pid']: p for p in processes}
    finished = 0
    n = len(processes)

    while finished < n:
        while arrivalIndex < n and processes[arrivalIndex]['arrival'] <= time:
            queues[0].append(processes[arrivalIndex])
            arrivalIndex += 1

        queueLevel = next((i for i, q in enumerate(queues) if q), None)

        if queueLevel is None:
            time += 1
            continue

        current = queues[queueLevel].pop(0)
        pid = current['pid']
        arrival = current['arrival']
        burstLeft = remaining[pid]

        if pid not in stats:
            stats[pid] = {
                'arrival': arrival,
                'burst': origBurst[pid],
                'startTime': time
            }

        quantum = queueQuantum[queueLevel]
        runTime = min(quantum, burstLeft)
        events.append((time, time + runTime, f"P{pid} (Q{queueLevel})"))
        time += runTime
        remaining[pid] -= runTime

        while arrivalIndex < n and processes[arrivalIndex]['arrival'] <= time:
            queues[0].append(processes[arrivalIndex])
            arrivalIndex += 1

        if remaining[pid] > 0:
            allotmentUsed[pid] += 1
            if allotmentUsed[pid] >= allotments[queueLevel] and queueLevel < totalQueues - 1:
                allotmentUsed[pid] = 0
                queues[queueLevel + 1].append(current)
            else:
                queues[queueLevel].append(current)
        else:
            stats[pid]['completeTime'] = time
            stats[pid]['turnaround'] = time - arrival
            stats[pid]['response'] = stats[pid]['startTime'] - arrival
            print(f"Process P{pid} finished:")
            print(f"  Arrival Time   : {arrival}")
            print(f"  Burst Time     : {origBurst[pid]}")
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
    print("\n=== Multi-Level Feedback Queue (MLFQ) Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = mlfq(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__main__":
    main()
