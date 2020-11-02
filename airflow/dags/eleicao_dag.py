import json
import redis
import datetime
from airflow import DAG
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

import requests
import json

default_args = {
        'owner'                 : 'airflow',
        'description'           : 'Use of the Python Operator',
        'depend_on_past'        : False,
        'start_date'            : datetime(2020, 10, 31),
        'email_on_failure'      : False,
        'email_on_retry'        : False,
        'retries'               : 1,
        'retry_delay'           : timedelta(seconds=30)
}

host = Variable.get("host")
index_path = Variable.get("index_path")
dados_path = Variable.get("dados_path")
eleicao = Variable.get("eleicao")
ufs = Variable.get("ufs", deserialize_json=True)

def download_index(**kwargs):
  files = []
  for uf in ufs:
    path = index_path.format(host=host, eleicao=eleicao, uf=uf)
    try:
      response = requests.get(path).json()  
      files += map(lambda arq: {
        "nm": f"{response['cdabr'].lower()}/{arq['nm']}",
        "dh": arq['dh']
      } , response['arq'])
    except:
      print(path)
      pass
  return files

def filter_variable_files_task(**kwargs):
    ti = kwargs['ti']
    files = ti.xcom_pull(task_ids='download_index')
    files = [file for file in files if file['nm'].endswith('-v.json')]
    return files

def filter_by_date_task(**kwargs):
  pool = redis.ConnectionPool(host='redis', port=6379, db=0)
  r = redis.Redis(connection_pool=pool)
  ti = kwargs['ti']

  files = ti.xcom_pull(task_ids='filter_variable_files_task')
  for file in files:
    if r.get(file['nm']) != file['dh'].encode('utf-8'):
      r.publish('files',json.dumps(file))


with DAG('eleicao_dag', default_args=default_args, schedule_interval="5 * * * *", catchup=False) as dag:
  dummy_task = DummyOperator(task_id='dummy_task', retries=3)
  download_index = PythonOperator(
        task_id='download_index',
        provide_context=True,
        python_callable=download_index,
        dag=dag,
        )

  filter_variable_files_task = PythonOperator(
        task_id='filter_variable_files_task',
        provide_context=True,
        python_callable=filter_variable_files_task,
        dag=dag,
        )

  filter_by_date_task = PythonOperator(
        task_id='filter_by_date_task',
        provide_context=True,
        python_callable=filter_by_date_task,
        dag=dag,
        )

  dummy_task >> \
    download_index >> \
      filter_variable_files_task >> \
        filter_by_date_task
