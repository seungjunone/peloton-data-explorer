# Extracting and Analyzing Peloton Data with Python


## Introduction
At the height of the COVID lockdown, a Peloton bike entered my life and quickly became my go-to cardio workout. Since then, I've explored their strength, rowing, and stretching classes, making Peloton a core part of my fitness routine. But just how "avid" a user am I? To find out, I decided to dive deep into my Peloton data and see what insights I could uncover.


## Structure

### Quick Guides
This series of Jupyter Notebooks in `quick-guides` directory provides a step-by-step guide to accessing, processing, and analyzing your Peloton data via the public API.  You'll learn how to connect to the API, extract data using various endpoints, and transform it into a usable format to perform insightful analyses. 

The notebooks are designed to be worked through sequentially, as later notebooks build upon the concepts, functions, and workflow established in earlier ones. While it's recommended to follow the series from start to finish, you are welcome to explore individual notebooks based on your specific interests.

The following table provides a brief overview of each notebook in the series:

| Notebook Title | Summary |
| --- | --- |
| [Peloton Public API Overview](./quick-guides/01_peloton-public-api-overview.ipynb) | This notebook introduces the Peloton public API and demonstrates how to authenticate and extract data. It uses the `requests` package for API calls and focuses on the user overview endpoint as a practical example for extraction and transformation. | 
| [User Overview End Point](./quick-guides/02_endpoint-user-overview.ipynb) | This notebook revisits the user overview endpoint, building upon the previous notebook. It introduces reusable functions for API calls and data transformation. Robust error handling and logging are incorporated to ensure graceful failure in case of issues. |


### Codes
The `codes` directory houses reusable functions developed and introduced in the Quick Start Guides. These functions are organized into modules based on their functionality, making them easy to locate and reuse in your analysis.  Leveraging these pre-built tools will significantly streamline your workflow and reduce code duplication.

| Function Category | Summary |
| --- | --- |
| [API Toolkit](./codes/peloton_api_toolkit.py) | Contains functions for interacting with the Peloton API. This includes functions for authentication, making requests to various endpoints (e.g., user overview, workout details), and handling pagination. |
| [Data Toolkit](./codes/peloton_data_toolkit.py) | Contains functions for cleaning, transforming, and preparing the data retrieved using the 
api_toolkit.  This includes functions for handling missing values, converting data types (e.g., timestamps), filtering data based on specific criteria, and performing other data manipulation tasks |


### Analysis


## Running Quick Guides on Jupyter Notebook

The quick-guides contains individual walkthrough that you can follow along on your machine. From terminal, 

1. Clone this repo and navigate to it.
1. `python3 -m venv .python` Create a virtual environment 
1. `source .python/bin/activate` Activate viertual environment created above
1. `pip install -r requirements.txt` Upgrade pip, the Python package installer, to the latest version within the activated virtual environment 
1. `pip install -r requirements.txt` Installs all the Python packages listed in the requirements.txt file within the activated virtual environment 
1. `Jupyter Notebook` Start the web server to run the notebook locally. By default, this will open the browser with Jupyter Notebook interface.

In quick-guides notebooks, Peloton credentials are loaded from environmental variable. You could save them locally in .bash_profile, and define it there.

To open `bash_profile` in Visual Studio:
```
code ~/.bash_profile
```

And add peloton credentials to bash_profile.
```
export peloton_user_name="{ your username }"
export peloton_password="{ your password }"
```
