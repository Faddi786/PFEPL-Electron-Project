# PFEPL-Electron-Project


Drone Survey Image Metadata Analysis System

Overview

This project addresses the challenge of ensuring compliance with drone camera configuration standards during large-scale drone surveys. The tool verifies and analyzes image metadata, helping pilots and the drone operations team maintain quality control. The system includes both an Electron-based desktop application (parent and child apps) and a planned web-based dashboard for comprehensive monitoring and analysis.
________________________________________
Problem Statement

Drone surveys, which involve capturing thousands of images per session for orthophoto generation, require precise camera configurations to ensure quality. However, pilots sometimes forget to set these configurations correctly, or camera systems automatically adjust settings like ISO, leading to deviations from standard values.
To tackle this, we created an image metadata analysis tool that:
1.	Analyzes image metadata from the drone survey images.
2.	Verifies compliance with specified configuration values.
3.	Generates a PDF report of the analysis.
4.	Provides detailed statistics, including the number of pass/fail images, and shares sample images with the back office.
   
The tool operates as a two-level architecture:
1.	Parent App: Used by drone department heads to create child apps for pilots.
2.	Child App: Used by pilots for image analysis.
Previously, only statistical summaries (pass/fail counts) were sent to managers and department heads. However, the drone department requested enhancements, Provide access to random samples of pass and fail images for each flight.

________________________________________
Technical Details
   
Technology Stack:
   
•	Electron Framework: JavaScript-based framework for cross-platform desktop apps.

•	Python Backend: For metadata extraction and analysis.

•	HTML/CSS/JS: For GUI development.

Requirements:

• Node.js

• Python and its packages 

________________________________________
Features and Workflow

Two-Level Architecture:
   
• Parent App: Generates child app installers and manages pilot accounts.

• Child App: Installed by pilots for analyzing images on their local systems.

Offline Functionality:
   
• Electron-based apps operate offline, ensuring compatibility with local file systems for direct access to images.

1.	Parent App Workflow:

    •	Register pilot details.

    •	Generate child app installer.

    •	Email the installer to pilots.

2.	Child App Workflow:

    •	Login and input the folder path of drone survey images.

    •	Perform metadata analysis.
  	
    •	Extracts metadata such as ISO, shutter speed, aperture, etc.

    •	Compares values against predefined standards to determine pass/fail status.

    •	Automatically generate PDF report for the pilot 

3.	Web Dashboard (Version 2):

    •	Access data from all child app analyses.

    •	View summary statistics, historical data, and sample images for each survey.
							
    •	Centralize and visualize data for the drone department team.

    •	Improved Reporting: Interactive charts and graphs for better insights.

    •	Update drone camera configurations dynamically by requesting data from server and updating in each child app

This project simplifies and standardizes the critical task of image metadata analysis for drone surveys, paving the way for improved operational efficiency and data quality.

