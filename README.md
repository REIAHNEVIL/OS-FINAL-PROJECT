# **OS PROJECT 1 - CPU SCHEDULING VISUALIZATION**

## **PROJECT OVERVIEW:**
This project is a CPU Scheduling Simulator designed to help users visualize and understand how various scheduling algorithms manage processes in an operating system. It combines a Python-based backend using Flask with a responsive frontend built using HTML, JavaScript, and CSS.

The simulator allows users to input or generate processes and simulate their execution under various scheduling strategies. It dynamically generates a Gantt chart to illustrate process execution over time.

<br>

## **HOW TO RUN THE SIMULATOR ITSELF?** 
Setup your Virtual Studio as follows:
<br>

<img width="1558" height="135" alt="Image" src="https://github.com/user-attachments/assets/90e94f06-7cae-4162-84b0-2008dfabd110" /> 
<br>
<br>

## **INSTRUCTIONS ON HOW TO RUN THE SIMULATION:**
<img width="341" height="958" alt="Image" src="https://github.com/user-attachments/assets/52959f74-6517-426e-b4fd-1fbf0b1aead6" />

### **1. You can add processes by:**
- Generating random values for each job by clicking on the **“Generate Button.”** Or,
- Manually inputting values for each job by entering data inside the **“Arrival Time”** input field and the** “Burst Time”** input field. Then, submit that data by clicking on the **“Save”** button to create a job. <br>


### **2. You can add Quantum time / Allotment time (for either RR/MLFQ) by:**
- Manually input value for quantum slice in **“Time Slice”** input field and submit this data by clicking on the **“Add Conditions”** button.
- Manually input value for allotment time in the **“Allotment”** input field and submit this data by clicking on the **“Add Conditions”** button.
- **_In MLFQ:_** Input values in **both input fields** and then click on the **“Add Conditions”** button.<br>


### **3. You can remove processes by:**
- Clicking on the **“Clear”** button that erases data within the input fields.<br>


### **4. You can select which algorithm to use by:**
- Using the dropdown menu to select the algorithm.
- Clicking on the **“Run”** button, this starts the process of the scheduler.
<img width="1043" height="71" alt="Image" src="https://github.com/user-attachments/assets/b5ff66d4-8f0b-4b26-8af9-a023c9a9be46" />
<img width="907" height="216" alt="Image" src="https://github.com/user-attachments/assets/f15ecc29-0cb1-4e5f-b30a-f3102e241d62" /><br>


### **5. You can remove all processes and data from the simulator by:**
- Clicking on the **“Clear”** button found beside the “Run” button.
<br>
<br>


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
**To simulate, we’ll use the following data for input:**<br>
 PID 1 = { Arrival Time: 0, Burst Time: 15 }<br>
 PID 2  = { Arrival Time: 0, Burst Time: 10 }<br>
 PID 3  = { Arrival Time: 1, Burst Time: 12 }<br>
 PID 4 =  = { Arrival Time: 1, Burst Time: 8 }<br>

QUANTUM SLICE: 2<br>
ALLOTMENT TIME: 3<br>
<br>

**Sample output for FIFO:**
<img width="1609" height="942" alt="Image" src="https://github.com/user-attachments/assets/9c69b41c-4e23-4b99-bb04-3687a73375b6" />
<img width="1577" height="142" alt="Image" src="https://github.com/user-attachments/assets/7a5b30fb-63d6-4020-8bce-eeee73b54ec2" />
<br>

**Sample output for SJF:**
<img width="1325" height="879" alt="Image" src="https://github.com/user-attachments/assets/6559e3f0-22e5-437b-848e-00b583a650aa" />
<img width="1582" height="140" alt="Image" src="https://github.com/user-attachments/assets/7f2c577e-f8bb-47c0-9713-cf7b9f5894ff" />
<br>

**Sample output for SRTF:**
<img width="1323" height="851" alt="Image" src="https://github.com/user-attachments/assets/39475d68-135d-44f4-87ed-c1afc0532192" />
<img width="1580" height="186" alt="Image" src="https://github.com/user-attachments/assets/f352cc4b-0952-4806-ba62-a3b57e0981d2" />
<br>

**Sample output for RR:**
<img width="1314" height="858" alt="Image" src="https://github.com/user-attachments/assets/af271f18-6af3-40d1-938f-6bc6a87d4384" />
<img width="1573" height="321" alt="Image" src="https://github.com/user-attachments/assets/6b3b22f6-9850-40b3-b104-d2d5cf268c4e" />
<br>

**Sample output for MLFQ:**
<img width="1328" height="868" alt="Image" src="https://github.com/user-attachments/assets/3cca5ed3-1e79-4a87-a302-03fcf2fe4f74" />
<img width="1575" height="324" alt="Image" src="https://github.com/user-attachments/assets/6e24b932-a945-4225-a0ac-942831593ae0" />
<br>
<br>


## **KNOWN BUGS, LIMITATIONS, OR INCOMPLETE FEATURES:**
- Clear button does not include the Average Metrics display.
  

## **MEMBER CONTRIBUTIONS:**

**1. Jure Rhoanne Q. Batohanon:**
- Backend Logic for SJF, SRTF, RR, and MLFQ

**2. Maria Katrina O. Esclamado:**
- Backend Logic for FIFO and GUI
