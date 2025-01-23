#!/bin/bash

# Define the name of the virtual environment directory
VENV_DIR="venv"

# Define the name of the Python script to run
SCRIPT_NAME="generator.py"

# Function to initialize the project
init() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi

    echo "Activating virtual environment..."
    source $VENV_DIR/bin/activate

    echo "Installing requirements..."
    pip install -r requirements.txt

    echo "Initialization completed."
}

# Function to start the Python script
start() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Virtual environment not found. Please run init command first."
        exit 1
    fi

    echo "Activating virtual environment..."
    source $VENV_DIR/bin/activate

    echo "Starting $SCRIPT_NAME..."
    python $SCRIPT_NAME &
}

# Function to stop the Python script
stop() {
    echo "Stopping $SCRIPT_NAME..."
    pkill -f $SCRIPT_NAME
}

# Check the command-line argument
case $1 in
    init)
        init
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 {init|start|stop}"
        exit 1
esac