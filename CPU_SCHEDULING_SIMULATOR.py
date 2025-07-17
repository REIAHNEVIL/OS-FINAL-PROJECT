#!/usr/bin/env python3
from collections import deque
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

def rr(processes):
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

def mlfq(processes):
    try:
        totalQueues = int(input("Enter the number of queues (minimum 4): "))
        if totalQueues < 4:
            print("Number of queues must be at least 4. Setting to default (4).")
            totalQueues = 4
    except ValueError:
        print("Invalid input. Setting number of queues to default (4).")
        totalQueues = 4

    print("\nConfigure time quantum and allotments for each level:")
    queueQuantum = []
    allotments = []
    for i in range(totalQueues):
        try:
            q = int(input(f"  TIME QUANTUM for Q{i} (default 1): ") or 1)
            a = int(input(f"  ALLOTMENT for Q{i} (default 1): ") or 1)
        except ValueError:
            print(f"[INVALID INPUT] for Q{i}. Using default values (1).")
            q, a = 1, 1
        queueQuantum.append(q)
        allotments.append(a)
    
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

            if 'startTime' not in stats[pid]:
                stats[pid]['startTime'] = time

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


def FIFOmain():
    print("\n=== FIFO Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = fifo(processes)

    printGantt(events)
    printStats(stats)

if __name__ == "__FIFOmain__":
   FIFOmain()

def SJFmain():
    print("\n=== Shortest Job First (SJF) Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = sjf(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__SJFmain__":
   SJFmain()

def SRTFmain():
    print("\n=== Shortest Remaining Time First (SRTF) Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = srtf(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__SRTFmain__":
   SRTFmain()

def RRmain():
    print("\n=== Round Robin Scheduling Simulation ===\n")
    processes = makeProcess()
    if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

    events, stats = rr(processes)
    printGantt(events)
    printStats(stats)

if __name__ == "__RRmain__":
   RRmain()

def MLFQmain():
     print("\n=== Multi-Level Feedback Queue (MLFQ) Scheduling Simulation ===\n")
     processes = makeProcess()
     if not processes:
        print("No processes to schedule. Exiting.")
        sys.exit(1)

     events, stats = mlfq(processes)
     printGantt(events)
     printStats(stats)

if __name__ == "__MLFQmain__":
    MLFQmain()

def main():
    choice = 0

    while choice != '6':
        print("\n=== CPU Scheduling Algorithm Selector ===")
        print("Choose an algorithm to simulate:")
        print("  [1] FIFO")
        print("  [2] SJF")
        print("  [3] SRTF")
        print("  [4] Round Robin (RR)")
        print("  [5] Multi-Level Feedback Queue (MLFQ)")
        print("  [6] Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        match choice:
            case '1':
                FIFOmain()

            case '2':
                SJFmain()

            case '3':
                SRTFmain()

            case '4':
                RRmain()

            case '5':
                MLFQmain()

            case '6':
                print("Exiting the simulator...")
                sys.exit(0)

            case _:
                print("Invalid choice. Please run again and select a number between 1 and 5.")

if __name__ == "__main__":
    main()