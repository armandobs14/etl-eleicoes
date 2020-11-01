import json
import redis
import requests

r = redis.Redis(host='redis', port=6379, db=0)
p = r.pubsub()

host = "palmaresfestlive.com.br"
eleicao = 8707
data_path = "https://{host}/ele2020/divulgacao/simulado/{eleicao}/dados/{arquivo}"

def get_fields(url):
    response = requests.get(url).json()
    print(response)

def custom_handler(message):
    data = json.loads(message['data'])
    r.set(data['nm'], data['dh'])
    get_fields(data_path.format(host=host, eleicao=eleicao, arquivo=data['nm']))

p.psubscribe(**{'files':custom_handler})
thread = p.run_in_thread(sleep_time=0.001)