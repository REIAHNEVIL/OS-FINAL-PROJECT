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
    print("Received data from frontend:", data)  # Debugging line

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
    print("Updated process list:", process_list)  # Debugging line

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
    print("Running scheduler with algorithm:", algorithm)  # Debugging line

    if algorithm == 'FIFO':
        events, stats = fifo(process_list)
    elif algorithm == 'SJF':
        events, stats = sjf(process_list)
    elif algorithm == 'SRTF':
        events, stats = srtf(process_list)
    elif algorithm == 'RR':
        quantum = int(request.args.get('quantum', 2))
        events, stats = rr(process_list, quantum)
    elif algorithm == 'MLFQ':
         q = conditions.get('quantum') or 1
         a = conditions.get('allotment') or 1
         total_queues = 4
         quantums = [q] * total_queues
         allotments = [a] * total_queues
         events, stats = mlfq(process_list, quantums, allotments)

    else:
        return jsonify({'error': 'Unknown algorithm'}), 400

    print("Scheduler output - Events:", events)
    print("Scheduler output - Stats:", stats)

    return jsonify({'events': events, 'stats': stats})

@app.route('/clear', methods=['POST'])
def clear():
    global process_list
    process_list = []
    print("Process list cleared.")  # Debugging line
    return jsonify({'status': 'cleared'})


# Store conditions globally (optional: put in a config or session later)



if __name__ == '__main__':
    app.run(debug=True)
