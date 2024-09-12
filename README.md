# Mouse Behavior Monitoring System

## Description

Monitoring the behavior of mice as an animal model plays a crucial role in medical research to understand diseases and test potential drugs. Two common methods used for this purpose are the **T Maze Spontaneous Alternation Test** and the **Plus Maze Test**, which assess mice's learning and memory levels, stress responses, and exploratory tendencies. However, manual observation can be time-consuming and prone to subjectivity. 

This research aims to improve research efficiency and objectivity by using video processing techniques. The experiment, conducted at **Sebelas Maret University**, utilizes **Artificial Intelligence (AI)** to detect and monitor mouse behavior in the **T Maze Spontaneous Alternation Test**.

The study involves the following steps:
1. Data collection on the mouse's behavior in the maze.
2. Labeling of the collected data for object detection purposes.
3. Training the data using **YOLOv8** (You Only Look Once) with the **Convolutional Neural Network (CNN)** method.

The trained model achieved an optimal accuracy level of **0.951** with a recall of **0.981**. Using this model, various computational algorithms were applied to detect key variables, such as the percentage of time spent on each maze arm, total distance covered, and switching time between arms.

### Key Results
This system enhances efficiency and objectivity in analyzing the **T Maze Spontaneous Alternation Test**. The research shows significant promise for advancing animal behavior research and can be further developed to explore neurological disorders and new therapies.

## Research Methodology

This study used an experimental method with qualitative data analysis. It was conducted at the **Faculty of Engineering** and **Faculty of Medicine**, Universitas Sebelas Maret.

### Research Method Diagram
![Figure 1 Research Method Diagram](https://github.com/Kyusane/MouseAnalysis/blob/main/Image/flowchart%20system.png)

## Hardware Design

In addition to the software model, a hardware design was created to support the tracking and monitoring system. The hardware components are arranged as follows:

### Hardware Design Diagram
![Figure 2 Hardware Design](https://github.com/Kyusane/MouseAnalysis/blob/main/Image/hardware.png)
