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

    // Prefer values from the new container first
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
        url += `&quantum=0`; // Ensure quantum is set to 0 for SJF and FCFS
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            updateResultsTable(data.stats);
            drawGanttChart(data.events);

            document.getElementById('quantumInfo').innerText =
                (algorithm === 'RR' && quantum)
                    ? `Quantum Time Slice: ${quantum}`
                    : '';
        });
}



function updateResultsTable(stats) {
    const tableBody = document.getElementById('resultsTableBody');
    tableBody.innerHTML = ''; // Clear old rows

    stats.forEach((proc) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.arrival}</td>
            <td>${proc.burst}</td>
            <td>
                <div class="progressContainer">
                    <div class="progressBar" id="progress-${proc.pid}">
                        <span id="progress-text-${proc.pid}" class="progress-label"></span>
                    </div>
                </div>
            </td>
            <td>${proc.completeTime ?? '-'}</td>
            <td>${proc.turnaround ?? '-'}</td>
            <td>${proc.response ?? '-'}</td>
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
    const pid = String(events.pid);

    chart.innerHTML = ''; // Clear previous chart

    const colors = ['#4caf50', '#2196f3', '#ff9800', '#e91e63', '#9c27b0', '#00bcd4', '#8bc34a'];
    const pidColorMap = {};
    let colorIndex = 0;

    if (!events || events.length === 0) return;

    const minStart = Math.min(...events.map(e => e.start));
    const maxEnd = Math.max(...events.map(e => e.end));
    const totalTime = maxEnd - minStart;
    const chartPixelWidth = 983;
    const pixelsPerUnit = chartPixelWidth / totalTime;

    events.forEach(event => {
        const duration = event.end - event.start;
        if (duration <= 0) return;

        const block = document.createElement('div');
        block.className = 'gantt-block';
        block.style.width = `${duration * pixelsPerUnit}px`;

        const pid = event.pid;

        if (!pidColorMap[pid]) {
            pidColorMap[pid] = colors[colorIndex % colors.length];
            colorIndex++;
        }

        block.style.backgroundColor = pid === 'idle' ? '#555' : pidColorMap[pid];
        block.innerText = pid === 'idle' ? 'Idle' : `P${pid}`;

        chart.appendChild(block);
    });
}


function clearProcesses() {
    fetch('/clear', { method: 'POST' })
        .then(res => res.json())
        .then(() => {
            document.getElementById('resultsTableBody').innerHTML = '';
            document.getElementById('ganttChart').innerHTML = '';
            doocument.getElementById('quantumInfo').innerText = '';
            document.getElementByID('timeSlice').value = '';
            document.getElementById('allotment').value = '';
        });
}
