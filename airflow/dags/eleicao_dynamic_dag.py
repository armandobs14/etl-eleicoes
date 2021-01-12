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

# Importando variáveis
config = Variable.get("config", deserialize_json=True)
host = config['host']
index_path = config['index_path']
dados_path = config['dados_path']
eleicao = config['eleicao']
ufs = config['ufs']

default_args = {
    'owner': 'airflow',
    'description': 'Use of the Python Operator',
    'depend_on_past': False,
    'start_date': datetime(2020, 10, 31),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

with DAG('eleicao_dynamic_dag', default_args=default_args, schedule_interval="*/18 * * * *", catchup=False) as dag:

    def print_kwargs(**kwargs):
        params = kwargs['params']
        print('Params are: {}'.format(params))

    def download_index(**kwargs):
        files = []
        path = index_path.format(host=host, eleicao=eleicao, uf=kwargs['uf'])
        try:
            response = requests.get(path).json()
            files += map(lambda arq: {
                "nm": f"{response['cdabr'].lower()}/{arq['nm']}",
                "dh": arq['dh']
            }, response['arq'])
        except:
            print(path)
            pass
        return files

    for uf in ufs:
        download_index_task = PythonOperator(
            task_id=f"dados_eleitorais_{uf}",
            python_callable=download_index,
            provide_context=True,
            op_kwargs={
                'uf': uf
            },
            dag=dag)
        
        kwargs_task = PythonOperator(
            task_id=f"kwargs_{uf}",
            python_callable=print_kwargs,
            provide_context=True,
            op_kwargs={
                'params': uf
            },
            dag=dag)
        
        download_index_task >> kwargs_task
