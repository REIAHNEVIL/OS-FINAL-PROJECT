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
        waitingTime = turnaroundTime - burst

        stats.append({
            'pid': pid,
            'arrival': arrival,
            'burst': burst,
            'executions': [{'start': startTime, 'duration': burst}],
            'completeTime': completeTime,
            'turnaround': turnaroundTime,
            'response': responseTime,
            'waiting': waitingTime
        })

        events.append({'pid': pid, 'start': startTime, 'end': completeTime})
        current = completeTime
    
        totalTurnaroundTime = sum(p['turnaround'] for p in stats)
        totalResponseTime = sum(p['response'] for p in stats)
        totalWaitingTime = sum(p['waiting'] for p in stats)
        averageMetrics = {
            'averageTurnaroundTime': totalTurnaroundTime / len(stats),
            'averageResponseTime': totalResponseTime / len(stats),
            'averageWaitingTime': totalWaitingTime / len(stats)
        }

    return events, stats, averageMetrics


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

            turnaround = end - arrival
            response = start - arrival
            waiting = turnaround - burst

            stats.append({
                'pid': pid,
                'arrival': arrival,
                'burst': burst,
                'executions': [{'start': start, 'duration': burst}],
                'completeTime': end,
                'turnaround': turnaround,
                'response': response,
                'waiting': waiting
            })

            events.append({'pid': pid, 'start': start, 'end': end})
            remaining = [p for p in remaining if p['pid'] != pid]
        else:
            nextArrival = min(p['arrival'] for p in remaining)
            events.append({'pid': 'idle', 'start': time, 'end': nextArrival})
            time = nextArrival
    
        totalTurnaroundTime = sum(p['turnaround'] for p in stats)
        totalResponseTime = sum(p['response'] for p in stats)
        totalWaitingTime = sum(p['waiting'] for p in stats)
        averageMetrics = {
            'averageTurnaroundTime': totalTurnaroundTime / len(stats),
            'averageResponseTime': totalResponseTime / len(stats),
            'averageWaitingTime': totalWaitingTime / len(stats)
        }

    return events, stats, averageMetrics


def srtf(processes):
    time = 0
    events = []
    stats_map = {}
    execution_logs = {}
    remaining = {p['pid']: p['burst'] for p in processes}
    finished = 0
    n = len(processes)
    arrived = []
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
                    events.append({'pid': current_process['pid'], 'start': last_switch, 'end': time})
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
                        'executions': [{'start' : last_switch, 'end' : current_process}],
                        'completeTime': None,
                        'turnaround': None,
                        'response': time - current_process['arrival'],
                        'waiting': None
                    }

            remaining[current_process['pid']] -= 1
            time += 1

            if remaining[current_process['pid']] == 0:
                events.append({'pid': current_process['pid'], 'start': last_switch, 'end': time})
                execution_logs.setdefault(current_process['pid'], []).append({
                    'start': last_switch,
                    'duration': time - last_switch
                })

                pid = current_process['pid']
                stats_map[pid]['completeTime'] = time
                stats_map[pid]['turnaround'] = time - current_process['arrival']
                stats_map[pid]['waiting'] = stats_map[pid]['turnaround'] - stats_map[pid]['burst']
                finished += 1
                current_process = None
        else:
            time += 1

        for pid, logs in execution_logs.items():
            stats_map[pid]['executions'] = logs

    statList = list(stats_map.values())

    totalTAT = sum(p['turnaround'] for p in statList)
    totalRT = sum(p['response'] for p in statList)
    totalWT = sum(p['waiting'] for p in statList)
    averageMetrics = {
        'averageTurnaroundTime': totalTAT / len(statList),
        'averageResponseTime': totalRT / len(statList),
        'averageWaitingTime': totalWT / len(statList)
    }
    return events, statList, averageMetrics


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
        for p in processes:
            if p['arrival'] == time:
                arrived.append(p)

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
        events.append({'start': time, 'end': time + execTime, 'pid': pid})

        time += execTime
        remaining[pid] -= execTime

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
            stats[pid]['waiting'] = stats[pid]['turnaround'] - stats[pid]['burst']

        stats[pid]['executions'] = stats.get(pid, {}).get('executions', []) + \
            [{'start': time - execTime, 'duration': execTime}]
        if remaining[pid] == 0:
            finished += 1

    statList = [stats[p['pid']] for p in processes]

    totalTAT = sum(p['turnaround'] for p in statList)
    totalRT = sum(p['response'] for p in statList)
    totalWT = sum(p['waiting'] for p in statList)
    averageMetrics = {
         'averageTurnaroundTime': totalTAT / len(statList),
         'averageResponseTime': totalRT / len(statList),
         'averageWaitingTime': totalWT / len(statList)
    }

    return events, statList, averageMetrics


def mlfq(processes, quantums, allotment):
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
                'pid': pid,
                'arrival': arrival,
                'burst': origBurst[pid],
                'startTime': time,
                'executions': []
            }

        runTime = min(quantums[queueLevel], burstLeft)
        events.append({'start': time, 'end': time + runTime, 'pid': pid})
        stats[pid]['executions'].append({'start': time, 'duration': runTime})

        time += runTime
        remaining[pid] -= runTime

        while arrivalIndex < n and processes[arrivalIndex]['arrival'] <= time:
            queues[0].append(processes[arrivalIndex])
            arrivalIndex += 1

        if remaining[pid] > 0:
            allotmentUsed[pid] += 1
            if allotmentUsed[pid] >= allotment[queueLevel] and queueLevel < totalQueues - 1:
                allotmentUsed[pid] = 0
                queues[queueLevel + 1].append(current)
            else:
                queues[queueLevel].append(current)
        else:
            stats[pid]['completeTime'] = time
            stats[pid]['turnaround'] = time - arrival
            stats[pid]['response'] = stats[pid]['startTime'] - arrival
            stats[pid]['waiting'] = stats[pid]['turnaround'] - stats[pid]['burst']
            finished += 1

    statList = [stats[p['pid']] for p in processes]
    totalTAT = sum(p['turnaround'] for p in statList)
    totalRT = sum(p['response'] for p in statList)
    totalWT = sum(p['waiting'] for p in statList)
    averageMetrics = {
        'averageTurnaroundTime': totalTAT / len(statList),
        'averageResponseTime': totalRT / len(statList),
        'averageWaitingTime': totalWT / len(statList)
    }

    return events, statList, averageMetrics

