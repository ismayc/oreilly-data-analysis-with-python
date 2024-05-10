# Materials for the course "Data Analysis with Python" for O'Reilly by Dr. Chester Ismay

## Recommended instructions on getting set up with Python and Jupyter Notebook

To help your students get their local machines set up for using Jupyter Notebooks along with pandas, matplotlib, seaborn, and plotly, you can provide the following step-by-step instructions. These will guide them through the installation of Python, necessary libraries, and setting up their development environment.

### Step 1: Install Python
1. **Download Python**: Go to the [official Python website](https://www.python.org/downloads/) and download the latest version of Python for your operating system (Windows, macOS, or Linux).
2. **Install Python**: Run the downloaded installer. Ensure that you check the box that says "Add Python to PATH" before clicking "Install Now."

### Step 2: Install Jupyter Notebook
1. **Open your command prompt (Windows) or terminal (macOS/Linux)**.
2. **Install Jupyter using pip**:
   ```bash
   pip install notebook
   ```

### Step 3: Install Required Libraries
1. **Install pandas, matplotlib, seaborn, and plotly**:
   ```bash
   pip install pandas matplotlib seaborn plotly
   ```

### Step 4: Launch Jupyter Notebook
1. **Open your command prompt or terminal**.
2. **Run Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```
   This command will open Jupyter Notebook in your default web browser.

### Step 5: Verify Installation
1. **Create a new notebook**: In the Jupyter Notebook interface, click on "New" and select "Python 3" to open a new notebook.
2. **Test the installation of the libraries**:
   - Import the libraries in the first cell of your notebook:
     ```python
     import pandas as pd
     import matplotlib.pyplot as plt
     import seaborn as sns
     import plotly.express as px
     ```
   - Run the cell (`Shift + Enter`). If no errors appear, the libraries are installed correctly.

### Additional Tips
- **Troubleshooting**: If you encounter any errors during installation, make sure that your pip is up to date (`pip install --upgrade pip`) and try the installation commands again. If issues persist, check for specific error messages online for troubleshooting tips.
- **Learning Resources**: Familiarize yourself with the Jupyter Notebook interface and basic functionality by reading tutorials or watching introductory videos about Jupyter Notebooks.
