#!/bin/bash
pip uninstall docker docker-py
pip install --user -r requirements.txt
airflow upgradedb
airflow scheduler &
airflow webserver
