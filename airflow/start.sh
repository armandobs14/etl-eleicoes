#!/bin/bash
python -m pip install --upgrade pip
pip uninstall docker docker-py
pip install --user -r requirements.txt
airflow db upgrade
airflow users create --username admin --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@example.org -p admin
airflow scheduler &
airflow webserver
