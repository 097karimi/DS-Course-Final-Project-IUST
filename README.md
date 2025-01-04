# DS-Course-Final-Project-IUST

Distributed Systems Project - University of IUST

This repository hosts my Distributed Systems Project for the Fall 2024 term at the University of IUST. The project focuses on designing and implementing a Real-Time Financial Analysis & Trading System using distributed systems principles.



📖 Project Overview

This project involves developing a scalable, distributed system that processes and analyzes simulated financial data in real-time. The system is designed to generate actionable trading signals through the integration of microservices, stream processing, and real-time data visualization.

Key Components:

1. Data Generator Script: Simulates financial data from multiple sources.
2. Data Ingestion Service: Receives, validates, and forwards data.
3. Stream Processing Service: Analyzes data and calculates trading indicators.
4. Trading Signal Service: Generates buy/sell signals.
5. Notification Service: Sends instant alerts on trading signals.
6. Visualization Service: Displays processed data and trading signals.
7. Load Balancer: Manages incoming traffic across servers.
8. Aggregator Service: Summarizes stock performance.




🛠️ Technologies Used

The project employs:

Microservices Architecture

Stream Processing for real-time data handling

Websockets for live updates

Load Balancing to handle high traffic

Visualization using modern web technologies like HTML, CSS, and JavaScript.



📊 Mandatory Trading Indicators

The system computes the following financial indicators:

1. Moving Average: Identifies trend directions.


2. Exponential Moving Average: Reacts quickly to price changes.


3. Relative Strength Index (RSI): Determines market overbought/oversold conditions.





🚀 Workflow

1. Data Generation: Simulated financial data creation.


2. Data Ingestion: Validation and forwarding of data.


3. Stream Processing: Calculation of indicators in real time.


4. Signal Generation: Production of actionable trading signals.


5. Notification: Alerts sent to users.


6. Data Aggregation: Summarization of stock data.


7. Visualization: Real-time display on a user-friendly dashboard.





🔧 Getting Started

Clone this repository.

Install dependencies listed in requirements.txt.

Use generator.py and manager.sh to simulate data generation and manage services.

Modify components as needed to customize the system.




🎯 Evaluation Criteria

Software Architecture: Adherence to microservices design.

Scalability: Handling increased workload efficiently.

Accuracy: Reliability of generated signals.

Usability: User-friendly dashboard and notifications.

Performance: Demonstrate throughput during presentations.




🌟 Bonus Features

1. Advanced Visualization: Interactive dashboard for financial data.


2. Real-World Dataset: Integration and testing with real datasets.


3. Distributed Caching: Implemented using tools like Redis to improve performance.





📂 Deliverables

1. Source Code: Well-documented and structured.


2. Project Report: Includes architecture and challenges.


3. Presentation: Demonstrates scalability and results.



Feel free to explore this project for educational purposes!
