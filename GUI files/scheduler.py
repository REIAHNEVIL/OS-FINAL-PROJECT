def fifo(processes):
    processes = sorted(processes, key=lambda p: (p['arrival'], p['pid']))
    current = 0
    events = []
    stats = []

    for p in processes:
        pid, arrival, burst = p['pid'], p['arrival'], p['burst']
        if current < arrival:
            events.append({'pid': 'idle', 'start': current, 'end': arrival})
            current = arrival

        startTime = current
        completeTime = startTime + burst
        turnaroundTime = completeTime - arrival
        responseTime = startTime - arrival

        stats.append({
            'pid': pid,
            'arrival': arrival,
            'burst': burst,
            'executions': [{'start': startTime, 'duration': burst }],
            'completeTime': completeTime,
            'turnaround': turnaroundTime,
            'response': responseTime
        })

        events.append({'pid': pid, 'start': startTime, 'end': completeTime})
        current = completeTime

    return events, stats


def sjf(processes):
    time = 0
    events = []
    stats = []
    remaining = processes.copy()

    while remaining:
        ready = [p for p in remaining if p['arrival'] <= time]
        if ready:
            current_proc = sorted(ready, key=lambda p: (p['burst'], p['arrival'], p['pid']))[0]
            pid, arrival, burst = current_proc['pid'], current_proc['arrival'], current_proc['burst']

            if time < arrival:
                events.append({'pid': 'idle', 'start': time, 'end': arrival})
                time = arrival

            start = time
            end = start + burst
            time = end

            stats.append({
                'pid': pid,
                'arrival': arrival,
                'burst': burst,
                'executions': [{ 'start':burst, 'duration':end}],
                'completeTime': end,
                'turnaround': end - arrival,
                'response': start - arrival
            })

            events.append({'pid': pid, 'start': start, 'end': end})
            remaining = [p for p in remaining if p['pid'] != pid]
        else:
            nextArrival = min(p['arrival'] for p in remaining)
            events.append({'pid': 'idle', 'start': time, 'end': nextArrival})
            time = nextArrival

    return events, stats

def srtf(processes):
    time = 0
    events = []
    stats_map = {}
    execution_logs = {}
    remaining = {p['pid']: p['burst'] for p in processes}
    finished = 0
    n = len(processes)
    arrived = []
    ready = []
    current_process = None
    last_switch = 0

    while finished < n:
        for p in processes:
            if p['arrival'] == time and p not in arrived:
                arrived.append(p)

        ready = [p for p in arrived if remaining[p['pid']] > 0 and p['arrival'] <= time]

        if ready:
            ready.sort(key=lambda p: (remaining[p['pid']], p['arrival'], p['pid']))
            next_process = ready[0]

            if current_process is None or current_process['pid'] != next_process['pid']:
                if current_process:
                    events.append({
                        'pid': current_process['pid'],
                        'start': last_switch,
                        'end': time
                    })
                    execution_logs.setdefault(current_process['pid'], []).append({
                        'start': last_switch,
                        'duration': time - last_switch
                    })

                current_process = next_process
                last_switch = time

                if current_process['pid'] not in stats_map:
                    stats_map[current_process['pid']] = {
                        'pid': current_process['pid'],
                        'arrival': current_process['arrival'],
                        'burst': current_process['burst'],
                        'executions': [],
                        'completeTime': None,
                        'turnaround': None,
                        'response': time - current_process['arrival']
                    }

            remaining[current_process['pid']] -= 1
            time += 1

            if remaining[current_process['pid']] == 0:
                events.append({
                    'pid': current_process['pid'],
                    'start': last_switch,
                    'end': time
                })
                execution_logs.setdefault(current_process['pid'], []).append({
                    'start': last_switch,
                    'duration': time - last_switch
                })
                stats_map[current_process['pid']]['completeTime'] = time
                stats_map[current_process['pid']]['turnaround'] = time - current_process['arrival']
                finished += 1
                current_process = None
        else:
            time += 1

    for pid, logs in execution_logs.items():
        stats_map[pid]['executions'] = logs

    return events, list(stats_map.values())  

def rr(processes, quantum=1):
    time = 0
    events = []
    stats = {}
    queue = []
    remaining = {p['pid']: p['burst'] for p in processes}
    arrived = []
    finished = 0
    n = len(processes)

    while finished < n:
        # Add processes arriving at current time
        for p in processes:
            if p['arrival'] == time:
                arrived.append(p)

        # Add to queue if not already in it and has remaining burst
        for p in arrived:
            if p['pid'] not in [q['pid'] for q in queue] and remaining[p['pid']] > 0:
                queue.append(p)

        if not queue:
            time += 1
            continue

        current = queue.pop(0)
        pid = current['pid']
        arrival = current['arrival']
        burstLeft = remaining[pid]

        if pid not in stats:
            stats[pid] = {
                'pid': pid,
                'arrival': arrival,
                'burst': current['burst'],
                'startTime': time
            }

        execTime = min(quantum, burstLeft)
        events.append({
            'start': time,
            'end': time + execTime,
            'pid': pid
        })

        time += execTime
        remaining[pid] -= execTime

        # Add newly arrived processes during this time quantum
        for p in processes:
            if time - execTime < p['arrival'] <= time:
                arrived.append(p)
                if p['pid'] not in [q['pid'] for q in queue] and remaining[p['pid']] > 0:
                    queue.append(p)

        if remaining[pid] > 0:
            queue.append(current)
        else:
            stats[pid]['executions'] = stats.get(pid, {}).get('executions', [])
            stats[pid]['completeTime'] = time
            stats[pid]['turnaround'] = time - arrival
            stats[pid]['response'] = stats[pid]['startTime'] - arrival
            finished += 1

    # Finalize stats list in the correct order
    stat_list = [stats[p['pid']] for p in processes]
    return events, stat_list

def mlfq(processes, quantums, allotments):
    totalQueues = len(quantums)

    processes.sort(key=lambda p: p['arrival'])
    origBurst = {p['pid']: p['burst'] for p in processes}
    arrivalIndex = 0
    allotmentUsed = {p['pid']: 0 for p in processes}
    time = 0
    events = []
    stats = {}
    queues = [[] for _ in range(totalQueues)]
    remaining = {p['pid']: p['burst'] for p in processes}
    finished = 0
    n = len(processes)

    while finished < n:
        # Add newly arrived processes to top queue
        while arrivalIndex < n and processes[arrivalIndex]['arrival'] <= time:
            queues[0].append(processes[arrivalIndex])
            arrivalIndex += 1

        # Find first non-empty queue
        queueLevel = next((i for i, q in enumerate(queues) if q), None)

        if queueLevel is None:
            time += 1
            continue

        current = queues[queueLevel].pop(0)
        pid = current['pid']
        arrival = current['arrival']
        burstLeft = remaining[pid]

        # Set initial stats if first time
        if pid not in stats:
            stats[pid] = {
                'arrival': arrival,
                'burst': origBurst[pid],
                'startTime': time,
                'executions': []
            }

        quantum = quantums[queueLevel]
        runTime = min(quantum, burstLeft)
        start = time
        end = time + runTime

        # Track execution segment
        stats[pid]['executions'].append({'start': start, 'duration': runTime})
        events.append({'pid': pid, 'start': start, 'end': end})

        time += runTime
        remaining[pid] -= runTime

        # Add new arrivals during runtime
        while arrivalIndex < n and processes[arrivalIndex]['arrival'] <= time:
            queues[0].append(processes[arrivalIndex])
            arrivalIndex += 1

        if remaining[pid] > 0:
            allotmentUsed[pid] += 1
            # Demote if exceeded allotment
            if allotmentUsed[pid] >= allotments[queueLevel] and queueLevel < totalQueues - 1:
                allotmentUsed[pid] = 0
                queues[queueLevel + 1].append(current)
            else:
                queues[queueLevel].append(current)
        else:
            stats[pid]['completeTime'] = time
            stats[pid]['turnaround'] = time - arrival
            stats[pid]['response'] = stats[pid]['startTime'] - arrival
            finished += 1

    # Format for frontend
    stats_list = []
    for pid, data in stats.items():
        stats_list.append({
            'pid': pid,
            'arrival': data['arrival'],
            'burst': data['burst'],
            'executions': [{'start': data['startTime'], 'duration': data['completeTime'] - data['startTime']}],
            'startTime': data['startTime'],
            'completeTime': data['completeTime'],
            'turnaround': data['turnaround'],
            'response': data['response']
        })

    return events, stats_list

           
