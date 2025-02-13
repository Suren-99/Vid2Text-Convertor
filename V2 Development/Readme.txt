Project Overview:
This project provides a solution for video processing, audio extraction, and text summarization using Python. It leverages various libraries to handle tasks such as extracting audio from video, converting the audio to text, and generating concise summaries.

Steps to Install Dependencies:

1) Install Python
Ensure you have Python installed on your system. You can download it from python.org.

2) (Optional) Create a Virtual Environment
It is recommended to create a virtual environment to keep your project dependencies isolated:

command : python -m venv venv

3) Install Required Libraries
Install the required dependencies by running the following command in your VS Code terminal:

command : pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

4) Download the LaMini-Flan-T5 Model
Download the MBZUAI/LaMini-Flan-T5-248M model for text summarization by running the following command:

command : git clone https://huggingface.co/MBZUAI/LaMini-Flan-T5-248M

5) Run the Application
Finally, run the application by executing this command in the VS Code terminal:

command : python app.py


