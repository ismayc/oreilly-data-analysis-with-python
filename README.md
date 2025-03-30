# Materials for the course "Data Analysis with Python" for O'Reilly by Dr. Chester Ismay

# Course content

The major files in this repository are
- `slides_2025-03.pdf`: PDF version of the slides used in this course to motivate the code.
- `economies.csv` and `economies.xlsx`: Two different versions of the same data for code walkthroughs, one as Comma-Separated Values and the other as a Microsoft Excel file
- `populations.csv` and `populations.xlsx`: Two different versions of the same data for student exercises.
- `exercises.ipynb`: A Jupyter Notebook with pseudocode/instructions provide to be filled in for code walkthroughs and student exercises
- `exercises_solutions.ipynb`: A Jupyter Notebook with answers to the code walkthroughs and exercises. An HTML version of these solutions is available at https://ismay-oreilly-dap.netlify.app/exercises_solutions.html and is the recommended way to view solutions.

## Recommended instructions on getting set up with Python and Jupyter Notebook

### Step 1: Install Python
- **Option 1: Anaconda Installation**:
  - **Download Anaconda**: Go to the [official Anaconda website](https://www.anaconda.com/products/distribution) and download the latest version of Anaconda for your operating system (Windows, macOS, or Linux). Anaconda conveniently installs Python, Jupyter Notebook, and many other commonly used packages for data science and machine learning.
- **Option 2: Python Installation**:
  - **Download Python**: Alternatively, you can download Python directly from the [official Python website](https://www.python.org/downloads/) and install the latest version for your operating system.

### Step 2: Launch Jupyter Notebook
- **Launch Jupyter Notebook**:
  - **Anaconda**: After installing Anaconda, open Anaconda Navigator from your Start Menu (Windows) or using the Anaconda Navigator application (macOS/Linux). In Anaconda Navigator, find Jupyter Notebook in the list of available applications and click on the "Launch" button. This will open Jupyter Notebook in your default web browser.
  - **Python Installation**: Open your command prompt (Windows) or terminal (macOS/Linux), and install Jupyter using pip:
    ```bash
    pip install notebook
    ```
    After installation, you can launch Jupyter Notebook by running:
    ```bash
    jupyter notebook
    ```

### Step 3: Install Required Libraries
- **Open Anaconda Prompt (Windows) or Terminal (macOS/Linux)** (if using Anaconda), or **open your command prompt (Windows) or terminal (macOS/Linux)** (if using Python installation).
- **Install Required Libraries using conda (Anaconda)**:
  ```bash
  conda install pandas matplotlib seaborn plotly openpyxl
  ```
- **Install Required Libraries using pip** (if not using Anaconda):
  ```bash
  pip install pandas matplotlib seaborn plotly openpyxl
  ```

### Step 4: Verify Installation
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
    
    # For plotly to load directly in Jupyter notebook
    import plotly.io as pio
    pio.renderers.default = 'iframe'
    ```
  - Run the cell (`Shift + Enter`). If no errors appear, the libraries are installed correctly.

### Additional Tips
- **Troubleshooting**: If you encounter any errors during installation, please ensure that Anaconda or Python is properly installed and up to date. If using Anaconda, you can also create a new environment and install the libraries within that environment.
- **Learning Resources**: Take advantage of Anaconda's integrated learning resources and documentation available through Anaconda Navigator. Additionally, familiarize yourself with the Jupyter Notebook interface and basic functionality by reading tutorials or watching introductory videos.
