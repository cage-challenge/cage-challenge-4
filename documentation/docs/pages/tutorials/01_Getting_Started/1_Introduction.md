# Installation Instructions

## Setup

The following are required software to begin the installation process:

- Git
- Python3 (recommended version 3.10)
- Pip

!!! tip "Virtual Environment"
    
    We recommend using a virtual environment running python 3.10 or later. 
    See '[Optional: Create a Virtual Environment](#optional-create-a-virtual-environment)' below' for instructions.

## Download

Clone the repository to your machine.

```
git clone >>>INSERT_URL_HERE<<<
```

## Optional: Create a Virtual Environment

A virtual environment is a self-contained virtual space within which you can download the required software dependencies for a relevant project without risking clashes with others. In this case, it allows your enviroment to be stable, disposable and reproducable. 

To create a virtual environment, you must first install the `virtualenv` module. 

Do so thusly:

```
pip install --user virtualenv
```

Once downloaded, create a venv using the following command:

```
python3 -m venv >>>PATH_TO_VENV<<<
```

`>>>PATH_TO_VENV<<<` is the directory you want to store the venv in.

To enable the venv:

```
source >>>PATH_TO_VENV<<</bin/activate
```

!!! tip "Done with CybORG?"
    
    Once you're done, you can disable the venv by simply running the command `deactivate`

## Requirements 

Install the dependencies (as listed in `Requirements.txt`), ensuring you are in the main directory.

```
pip install -r Requirements.txt
```

Locally install CybORG.

!!! warning "Don't run the following command with `sudo`"
    
```
pip install -e .
```

Install the Tcl/Tk GUI toolkit tkinter:

```
sudo apt install python3-tk --assume-yes
```

## Testing your Install

Run the following tests to check you've installed CybORG correctly.

```
pytest ./CybORG/Tests/test_cc4
```