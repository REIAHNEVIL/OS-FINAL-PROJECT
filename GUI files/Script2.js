let lastStats = [];
let lastEvents = [];
let lastAverageMetrics = {};


document.getElementById('processForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    const arrival = formData.get('arrival');
    const burst = formData.get('burst');

    fetch('/add_process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ arrival, burst })
    })
        .then(res => res.json())
        .then(data => {
            console.log('Process added:', data);

            const tableBody = document.getElementById('resultsTableBody');
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${data.pid || 'P?'}</td>
                <td>${arrival}</td>
                <td>${burst}</td>
                <td>Pending</td>
                <td>-</td>
                <td>-</td>
                <td>-</td>
            `;
            tableBody.appendChild(newRow);
            document.getElementById('averageMetrics').innerHTML = '';

        });
});

document.getElementById('generateRandom').addEventListener('click', function () {
    fetch('/generate_random')
        .then(res => res.json())
        .then(data => {
            console.log('Generated random values:', data);
            document.getElementById('arrivalInput').value = data.arrival;
            document.getElementById('burstInput').value = data.burst;
        });
});


document.getElementById('addTime').addEventListener('click', function () {
    const algorithm = document.getElementById('algorithm').value;
    const quantum = document.getElementById('newTimeSlice')?.value;
    const allotment = document.getElementById('newAllotment')?.value;

    const body = {
        algorithm: algorithm,
        quantum: quantum,
        allotment: allotment
    };

    fetch('/set_conditions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
        .then(res => res.json())
        .then(data => {
            alert(data.message || 'New conditions set!');
        });
});


function runScheduler() {
    const algorithm = document.getElementById('algorithm').value;
    const quantum = document.getElementById('newTimeSlice')?.value || document.getElementById('timeSlice')?.value;
    const allotment = document.getElementById('newAllotment')?.value || document.getElementById('allotment')?.value;

    let url = `/run_scheduler?algorithm=${algorithm}`;

    if (algorithm === 'RR' && quantum) {
        url += `&quantum=${quantum}`;
    }

    if (algorithm === 'MLFQ' && quantum && allotment) {
        const quantumArray = quantum.split(',').map(q => `quantum=${q.trim()}`).join('&');
        const allotmentArray = allotment.split(',').map(a => `allotment=${a.trim()}`).join('&');
        url += `&${quantumArray}&${allotmentArray}`;
    }

    if (algorithm === 'RR' && !quantum) {
        alert("Please enter a time slice (quantum) for RR.");
        return;
    }
    if (algorithm === 'MLFQ' && (!quantum || !allotment)) {
        alert("Please enter quantum and allotment values for MLFQ.");
        return;
    }
    if (algorithm === 'SJF' || algorithm === 'FCFS') {
        url += `&quantum=0`; 
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            updateResultsTable(data.stats);
            drawGanttChart(data.events);
            displayAverageMetrics(data.averageMetrics);

            const quantumInfo = document.getElementById('quantumInfo');
            const allotmentInfo = document.getElementById('allotmentInfo'); 

            if (algorithm == RR) {
                quantumInfo.innerText = `Quantum Time Slice: ${quantum}`;
                timeSlice.innerText = '';
            } else if (algorithm == MLFQ) {
                quantumInfo.innerText = `Quantum Time Slice: ${quantum}`;
                allotmentInfo.innerText = `Allotment Time: ${allotment}`;
            }

        });


    fetch(url)
        .then(res => res.json())
        .then(data => {
            lastStats = data.stats;
            lastEvents = data.events;
            lastAverageMetrics = data.averageMetrics;

            updateResultsTable(data.stats);
            drawGanttChart(data.events);
            displayAverageMetrics(data.averageMetrics);
        });


}



function updateResultsTable(stats) {
    const tableBody = document.getElementById('resultsTableBody');
    tableBody.innerHTML = ''; 

    stats.forEach((proc) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.arrival}</td>
            <td>${proc.burst}</td>
            <td>
                <div class="progressContainer">
                    <div class="progressBar" id="progress-${proc.pid}">
                    </div>
                </div>
            </td>
            <td>${proc.completeTime ?? '-'}</td>
            <td>${proc.turnaround ?? '-'}</td>
            <td>${proc.response ?? '-'}</td>
            <td>${proc.waiting ?? '-'}</td>
        `;
        tableBody.appendChild(row);

        const bar = document.getElementById(`progress-${proc.pid}`);
        const text = document.getElementById(`progress-text-${proc.pid}`);

        let totalFilled = 0;
        const timeUnit = 200;

        if (Array.isArray(proc.executions)) {
            proc.executions.forEach((segment) => {
                const startDelay = segment.start * timeUnit;
                const segmentDuration = segment.duration * timeUnit;
                const percent = (segment.duration / proc.burst) * 100;

                setTimeout(() => {
                    totalFilled += percent;

                    bar.style.transition = `width ${segmentDuration}ms linear`;
                    bar.style.width = `${totalFilled}%`;

                    if (text) {
                        text.textContent = `${Math.floor(totalFilled)}%`;
                    }
                }, startDelay);
            });
        }
    });
}
function drawGanttChart(events) {
    const chart = document.getElementById('ganttChart');
    chart.innerHTML = '';

    const colors = ['#4caf50', '#2196f3', '#ff9800', '#e91e63', '#9c27b0', '#00bcd4', '#8bc34a'];
    const pidColorMap = {};
    let colorIndex = 0;

    if (!events || events.length === 0) return;

    const minStart = Math.min(...events.map(e => e.start));
    const maxEnd = Math.max(...events.map(e => e.end));
    const totalTime = maxEnd - minStart;
    const chartPixelWidth = 983;
    const pixelsPerUnit = chartPixelWidth / totalTime;

    let lastEndTime = null;

    events.forEach((event, index) => {
        const duration = event.end - event.start;
        if (duration <= 0) return;

        const block = document.createElement('div');
        block.className = 'gantt-block';
        block.style.width = `${duration * pixelsPerUnit}px`;
        block.style.backgroundColor = event.pid === 'idle' ? '#555' : (
            pidColorMap[event.pid] ?? (pidColorMap[event.pid] = colors[colorIndex++ % colors.length])
        );
        block.style.color = 'white';
        block.style.fontSize = '10px';
        block.style.textAlign = 'center';
        block.style.padding = '2px';
        block.style.position = 'relative';

        if (event.pid === 'idle') {
            block.innerText = 'Idle';
        } else {
            block.innerText = event.queueLevel !== undefined
                ? `P${event.pid} (Q${event.queueLevel})`
                : `P${event.pid}`;
        }

        const timeLabel = document.createElement('div');
        timeLabel.style.position = 'absolute';
        timeLabel.style.bottom = '-16px';
        timeLabel.style.left = '0';
        timeLabel.style.fontSize = '14px';
        timeLabel.style.width = '100%';
        timeLabel.style.display = 'flex';
        timeLabel.style.justifyContent = 'space-between';

        const startLabel = (lastEndTime !== event.start) ? `<span>${event.start}</span>` : `<span></span>`;
        timeLabel.innerHTML = `${startLabel}<span>${event.end}</span>`;

        lastEndTime = event.end;

        block.appendChild(timeLabel);
        chart.appendChild(block);
    });
}



function displayAverageMetrics(averageMetrics) {
    const average = document.getElementById('averageMetrics');
    average.style.display = 'flex';
    average.style.gap = '20px';
    console.log('Average Metrics:', averageMetrics);
    average.innerHTML = `
        <p>Average Turnaround Time: ${averageMetrics.averageTurnaroundTime.toFixed(2)}</p>
        <p>Average Waiting Time: ${averageMetrics.averageWaitingTime.toFixed(2)}</p>
        <p>Average Response Time: ${averageMetrics.averageResponseTime.toFixed(2)}</p>
    `;
}

function extractResults() {
    const tableBody = document.getElementById('resultsTableBody');

    if (!tableBody || tableBody.rows.length === 0) {
        alert("No results available to extract.");
        return;
    }

    fetch('/extract_results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            stats: lastStats,
            events: lastEvents,
            averageMetrics: lastAverageMetrics
        })
    })
        .then(res => res.json())
        .then(data => {
            const a = document.createElement('a');
            a.href = data.url;
            a.download = 'results.txt';
            a.click();
        })
        .catch(err => console.error('Extract failed:', err));
}

function clearProcesses() {
    fetch('/clear', { method: 'POST' })
        .then(res => res.json())
        .then(() => {
            document.getElementById('resultsTableBody').innerHTML = '';
            document.getElementById('ganttChart').innerHTML = '';
            document.getElementById('quantumInfo').innerText = '';
            document.getElementById('timeSlice').value = '';
            document.getElementById('allotment').value = '';
            document.getElementById('averageMetrics').innerHTML = '';
        });
}
