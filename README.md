# **OS PROJECT 1 - CPU SCHEDULING VISUALIZATION**

## **PROJECT OVERVIEW:**
This project is a CPU Scheduling Simulator designed to help users visualize and understand how various scheduling algorithms manage processes in an operating system. It combines a Python-based backend using Flask with a responsive frontend built using HTML, JavaScript, and CSS.

The simulator allows users to input or generate processes and simulate their execution under various scheduling strategies. It dynamically generates a Gantt chart to illustrate process execution over time.


## **INSTRUCTIONS ON HOW TO RUN THE SIMULATION:**
### **You can add processes by:**
- Generating random values for each job by clicking on the “Generate Button.” Or,
- Manually inputting values for each job by entering data inside the “Arrival Time” input field and the “Burst Time” input field. Then, submit that data by clicking on the “Save” button to create a job. 

### **You can add Quantum time / Allotment time (for either RR/MLFQ) by:**
- Manually input value for quantum slice in **“Time Slice”** input field and submit this data by clicking on the **“Add Conditions”** button.
- Manually input value for allotment time in the **“Allotment”** input field and submit this data by clicking on the **“Add Conditions”** button.
- **_In MLFQ:_** Input values in **both input fields** and then click on the **“Add Conditions”** button.

### **You can remove processes by:**
- Clicking on the **“Clear”** button that erases data within the input fields.
  
### **You can select which algorithm to use by:**
- Using the dropdown menu to select the algorithm.
- Clicking on the **“Run”** button, this starts the process of the scheduler.

### **You can remove all processes and data from the simulator by:**
- Clicking on the **“Clear”** button found beside the “Run” button.
  

## **SCHEDULING ALGORITHMS USED IN THIS SIMULATION:**
**1. FIFO (First-In-First-Out)**
- Processes are scheduled in the exact order they arrive. The first process to arrive gets the CPU first, and runs to completion.
- Non-preemptive

**2. SJF (Shortest Job First)**
- Selects the process with the shortest burst time from the ready queue. Only processes that have arrived are considered.
-  Non-preemptive

**3. SRTF (Shortest Remaining Time FIrst)**
- A preemptive version of SJF. At every time unit, the scheduler picks the process with the shortest remaining burst time.
- Preemptive

**4. RR (Round Robin)**
- Each process is assigned a fixed time slice (quantum). After the quantum expires, the CPU is given to the next ready process.
- Preemptive

**5. MLFQ (Multi-Level Feedback Queue)**
- Uses multiple queues with different priority levels and time quanta. Processes start in the highest-priority queue and are demoted if they use too much CPU time.
- Highly dynamic and adaptive


## **TERMINAL OUTPUT EXAMPLES (Sample input and expected output):**


## **KNOWN BUGS, LIMITATIONS, OR INCOMPLETE FEATURES:**
- Clear button does not include the Average Metrics display.
  

## **MEMBER CONTRIBUTIONS:**

**1. Jure Rhoanne Q. Batohanon:**
- Backend Logic for SJF, SRTF, RR, and MLFQ

**2. Maria Katrina O. Esclamado:**
- Backend Logic for FIFO and GUI
