import os
import json
import redis
import requests

r = redis.Redis(host='redis', port=6379, db=0)
p = r.pubsub()

host = os.environ['HOST']
eleicao = os.environ['ELEICAO']
data_path = "https://{host}/ele2020/divulgacao/simulado/{eleicao}/dados/{arquivo}"

def download_file(url):
    r = requests.get(url)
    file_name = url.split('/')[-1]
    print(f"saving {file_name}")
    with open(f"/tmp/nginx/{file_name}", 'wb') as f:
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
