from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.hooks.redis_hook import RedisHook
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow import DAG
import requests
import json

# Importando variáveis
config = Variable.get("config", deserialize_json=True)
host = config['host']
index_path = config['index_path']
dados_path = config['dados_path']
eleicao = config['eleicao']
ufs = config['ufs']

redis_hook = RedisHook()

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

def download_index(**kwargs):
        redis = redis_hook.get_conn()
        path = index_path.format(host=host, eleicao=eleicao, uf=kwargs['uf'])
        response = requests.get(path).json()

        for arq in response['arq']:
            file = {
                "nm": f"{response['cdabr'].lower()}/{arq['nm']}",
                "dh": arq['dh']
            }
            if redis.get(file['nm']) !=  file['dh'].encode('utf-8'):
                redis.publish('files',json.dumps(file))

with DAG('eleicao_dynamic_dag', default_args=default_args, schedule_interval="*/18 * * * *", catchup=False) as dag:
    
    for uf in ufs:
        download_index_task = PythonOperator(
            task_id=f"dados_eleitorais_{uf}",
            python_callable=download_index,
            provide_context=True,
            op_kwargs={
                'uf': uf
            },
            dag=dag)
