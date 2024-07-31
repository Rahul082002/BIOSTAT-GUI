# CG-STAT Electrochemical GUI

This project is a Tkinter-based GUI application designed to run electrochemical processes (CV and DPV) on a Raspberry Pi. The GUI allows users to input parameters, initiate processes, and visualize results.

## Features

- **User-Friendly Interface**: Easily input parameters for electrochemical processes.
- **Process Control**: Start CV or DPV processes remotely on a Raspberry Pi.
- **Real-Time Visualization**: Fetch and display results in graphical format.
- **Remote Data Handling**: Securely transfer data and execute commands via SSH.

## Prerequisites

- Raspberry Pi with the necessary electrochemical software installed.
- Python 3.x installed on both the Raspberry Pi and the local machine.
- Libraries: Tkinter, Paramiko, Matplotlib, OpenCV, PIL.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/CG-STAT-Electrochemical-GUI.git
   cd CG-STAT-Electrochemical-GUI
