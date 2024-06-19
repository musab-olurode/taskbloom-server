<!-- Add a proper redame content that covers installing python, setting up a virtual environment, running migrations, creating, a superuser, and then running the app -->

# Django Task Management System

This is a task management system built with Django.

## Prerequisites

- Python 3.8 or higher

## Installation

1. **Install Python**

   Download Python from the official website [https://www.python.org/downloads/](https://www.python.org/downloads/) and install it.

2. **Set up a virtual environment**

   Open a terminal and navigate to the project directory, then run the following commands:

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**

- On Windows:

  ```bash
  .\env\Scripts\activate
  ```

- On macOS and Linux:

  ```bash
  source env/bin/activate
  ```

4. **Install the project dependencies**

   ```bash
    pip install -r requirements.txt
   ```

5. **Run the migrations**

   ```bash
    python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
    python manage.py createsuperuser
   ```

7. **Run the development server**

   ```bash
    python manage.py runserver
   ```

8. **Access the application**

   Open your browser and navigate to [http://localhost:8000/](http://localhost:8000/).
