# Materials for the course "Data Analysis with Python" for O'Reilly by Dr. Chester Ismay

# Course content

The major files in this repository are
- `economies.csv` and `economies.xlsx`: Two different versions of the same data for code walkthroughs, one as Comma-Separated Values and the other as a Microsoft Excel file
- `populations.csv` and `populations.xlsx`: Two different versions of the same data for student exercises.
- `exercises.ipynb`: A Jupyter Notebook with pseudocode/instructions provide to be filled in for code walkthroughs and student exercises
- `exercises_solutions.ipynb`: A Jupyter Notebook with answers to the code walkthroughs and exercises. An HTML version of these solutions is available at https://ismay-oreilly-dap.netlify.app/exercises_solutions.html and is the recommended way to view solutions.

## Recommended instructions on getting set up with Python and Jupyter Notebook

### Step 1: Install Python
- **Download Python**: Go to the [official Python website](https://www.python.org/downloads/) and download the latest version of Python for your operating system (Windows, macOS, or Linux).

### Step 2: Install Jupyter Notebook
- **Open your command prompt (Windows) or terminal (macOS/Linux)**.
- **Install Jupyter using pip**:
   ```bash
   pip install notebook
   ```

### Step 3: Install Required Libraries
- **Install pandas, matplotlib, seaborn, and plotly**:
   ```bash
   pip install pandas matplotlib seaborn plotly
   ```

### Step 4: Launch Jupyter Notebook
- **Open your command prompt or terminal**.
- **Run Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```
   This command will open Jupyter Notebook in your default web browser.

### Step 5: Verify Installation
- **Create a new notebook**: In the Jupyter Notebook interface, click on "New" and select "Python 3" to open a new notebook.
- **Test the installation of the libraries**:
   - Import the libraries in the first cell of your notebook:
     ```python
     import pandas as pd
     import matplotlib.pyplot as plt
     import seaborn as sns
     import plotly.express as px
     import plotly.graph_objects as go
     from plotly.subplots import make_subplots
     ```
   - Run the cell (`Shift + Enter`). If no errors appear, the libraries are installed correctly.

### Additional Tips
- **Troubleshooting**: If you encounter any errors during installation, make sure that your pip is up to date (`pip install --upgrade pip`) and try the installation commands again. If issues persist, check for specific error messages online for troubleshooting tips.
- **Learning Resources**: Familiarize yourself with the Jupyter Notebook interface and basic functionality by reading tutorials or watching introductory videos about Jupyter Notebooks.
