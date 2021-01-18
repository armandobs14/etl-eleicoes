import os
import json
import redis
import requests

r = redis.Redis(host='redis', port=6379, db=0)
p = r.pubsub()

host = os.environ['HOST']
eleicao = os.environ['ELEICAO']
data_path = "https://{host}/ele2020/divulgacao/simulado/{eleicao}/dados/{arquivo}"


for format in ['json','sig','cer']:
    path = f"/tmp/nginx/{format}"
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url):
    r = requests.get(url)
    file_name = url.split('/')[-1]
    extension = file_name.split('.')[-1]
    with open(f"/tmp/nginx/{extension}/{file_name}", 'wb') as f:
        f.write(r.content)

def custom_handler(message):
    data = json.loads(message['data'])
    try:
        download_file(data_path.format(host=host, eleicao=eleicao, arquivo=data['nm']))
        r.set(data['nm'], data['dh'])
    except:
        print(f"Não foi possível baixar arquivo {data['nm']}")

print("Starting client")
p.psubscribe(**{'files':custom_handler})
thread = p.run_in_thread(sleep_time=0.001)
