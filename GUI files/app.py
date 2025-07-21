from flask import Flask, render_template, request, jsonify
from scheduler import fifo, sjf, srtf, rr, mlfq

app = Flask(__name__)
process_list = []

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/add_process', methods=['POST'])
def add_process():
    data = request.get_json()
    print("Received data from frontend:", data) 

    try:
        arrival = int(data.get('arrival'))
        burst = int(data.get('burst'))
    except (TypeError, ValueError) as e:
        print("Error parsing arrival/burst:", e)
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

    process = {
        'pid': len(process_list) + 1,
        'arrival': arrival,
        'burst': burst
    }
    process_list.append(process)
    print("Updated process list:", process_list)  

    return jsonify({'status': 'success', 'processes': process_list})

conditions = {
    'quantum': None,
    'allotment': None
}

@app.route('/set_conditions', methods=['POST'])
def set_conditions():
    global conditions
    data = request.get_json()
    print("Received conditions:", data)

    try:
        quantum = int(data.get('quantum', 1))
        allotment = int(data.get('allotment', 1))
        conditions['quantum'] = quantum
        conditions['allotment'] = allotment
        return jsonify({'message': 'Quantum and Allotment set successfully'})
    except (TypeError, ValueError) as e:
        print("Error setting conditions:", e)
        return jsonify({'error': 'Invalid quantum or allotment'}), 400
    

@app.route('/run_scheduler', methods=['GET'])
def run_scheduler():
    algorithm = request.args.get('algorithm')
    print("Running scheduler with algorithm:", algorithm) 

    if algorithm == 'FIFO':
        events, stats, averageMetrics = fifo(process_list)
    elif algorithm == 'SJF':
        events, stats, averageMetrics = sjf(process_list)
    elif algorithm == 'SRTF':
        events, stats, averageMetrics = srtf(process_list)
    elif algorithm == 'RR':
        quantum = int(request.args.get('quantum', 2))
        events, stats, averageMetrics = rr(process_list, quantum)
    elif algorithm == 'MLFQ':
         q = int(request.args.get('quantum', 2)) 
         a = int(request.args.get('allotment', 1))
         total_queues = 4
         quantums = [q] * total_queues
         allotment = [a] * total_queues
         events, stats, averageMetrics = mlfq(process_list, quantums, allotment)

    else:
        return jsonify({'error': 'Unknown algorithm'}), 400

    print("Scheduler output - Events:", events)
    print("Scheduler output - Stats:", stats)
    print("Scheduler output - Average Metrics:", averageMetrics)

    return jsonify({'events': events, 'stats': stats , 'averageMetrics' : averageMetrics})

@app.route('/clear', methods=['POST'])
def clear():
    global process_list
    process_list = []
    print("Process list cleared.")  
    return jsonify({'status': 'cleared'})

import random  

@app.route('/generate_random', methods=['GET'])
def generate_random():
    arrival = random.randint(0, 10)
    burst = random.randint(1, 10)
    print(f"Generated random arrival: {arrival}, burst: {burst}")
    return jsonify({'arrival': arrival, 'burst': burst})


@app.route('/extract_results', methods=['POST'])
def extract_results():
    data = request.get_json()

    stats = data.get('stats', [])
    events = data.get('events', [])
    averages = data.get('averageMetrics', {})

    lines = []

    lines.append("Process Stats:")
    for proc in stats:
        lines.append(
            f"P{proc['pid']} | Arrival: {proc['arrival']}, Burst: {proc['burst']}, "
            f"Complete: {proc.get('completeTime', '-')}, TAT: {proc.get('turnaround', '-')}, "
            f"WT: {proc.get('waiting', '-')}, RT: {proc.get('response', '-')}"
        )

    lines.append("\nGantt Chart Events:")
    for ev in events:
        q = f"Q{ev['queue']}" if 'queue' in ev else ''
        lines.append(f"{ev['start']} to {ev['end']}: P{ev['pid']} {q}".strip())

    lines.append("\nAverage Metrics:")
    lines.append(f"Average Turnaround Time: {averages.get('averageTurnaroundTime', 0):.2f}")
    lines.append(f"Average Waiting Time: {averages.get('averageWaitingTime', 0):.2f}")
    lines.append(f"Average Response Time: {averages.get('averageResponseTime', 0):.2f}")

    file_path = os.path.join("static", "results.txt")
    with open(file_path, "w") as f:
        f.write("\n".join(lines))

    return jsonify({"url": f"/static/results.txt"})
import os




if __name__ == '__main__':
    app.run(debug=True)