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
To achieve this, the system consists of:
•	Desktop Applications for image metadata analysis (offline functionality).
•	A planned web-based platform to centralize and enhance data visualization and access.
________________________________________
Features
Desktop Applications (Electron Framework)
1.	Parent App (Drone Operations HQ):
o	Allows drone department heads to register users (pilots) with details like ID, password, and email.
o	Generates a Child App installer to send to the pilots via email.
2.	Child App (For Pilots):
o	Login to access the tool.
o	Input the folder containing images captured during the drone survey.
o	Analyzes image metadata for compliance with specified camera configurations.
o	Provides:
	PDF Report: A detailed document with analysis results for the pilot.
	Back Office Statistics: Summarized data (e.g., total images, pass/fail counts).
	Sample Images: Randomly selected 5 pass and 5 fail images for quality review.
________________________________________
Web-Based Dashboard (Planned for Version 2)
•	Enables drone operations employees to log in and access detailed analysis data.
•	Features:
o	View metadata analysis statistics.
o	Display random sample images for pass/fail categories.
o	Store and organize historical analysis data for tracking and review.
________________________________________
Technical Details
1.	Offline Functionality:
o	Electron-based apps operate offline, ensuring compatibility with local file systems for direct access to images.
2.	Two-Level Architecture:
o	Parent App: Generates child app installers and manages pilot accounts.
o	Child App: Installed by pilots for analyzing images on their local systems.
3.	Image Metadata Analysis:
o	Extracts metadata such as ISO, shutter speed, aperture, etc.
o	Compares values against predefined standards to determine pass/fail status.
4.	Technology Stack:
o	Electron Framework: JavaScript-based framework for cross-platform desktop apps.
o	Python Backend: For metadata extraction and analysis.
o	HTML/CSS/JS: For GUI development.
________________________________________
Workflow
1.	Parent App Workflow:
o	Register pilot details.
o	Generate child app installer.
o	Email the installer to pilots.
2.	Child App Workflow:
o	Login and input the folder path of drone survey images.
o	Perform metadata analysis.
o	Generate:
	PDF report for the pilot.
	Back office statistics with sample images.
3.	Web Dashboard (Version 2):
o	Access data from all child app analyses.
o	View summary statistics, historical data, and sample images for each survey.
________________________________________
Requirements
•	Nothing
________________________________________
Benefits
•	Ensures compliance with camera configuration standards during drone surveys.
•	Automates metadata analysis, reducing manual effort.
•	Provides actionable insights to both pilots and the drone operations team.
•	Enhances back-office review with detailed statistics and sample image analysis.
•	Offline functionality ensures compatibility in fieldwork scenarios.
________________________________________
Future Enhancements (Version 2)
•	Web Dashboard: To centralize and visualize data for the drone department team.
•	Improved Reporting: Interactive charts and graphs for better insights.
This project simplifies and standardizes the critical task of image metadata analysis for drone surveys, paving the way for improved operational efficiency and data quality.

