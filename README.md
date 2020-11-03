# etl-eleicoes
ETL para consumo dos dados de eleições do TSE

## Soluções utilizadas
Abaixo temos as aplicações utilizadas na solução e a motivação para cada uma delas
- Apache airflow
  - orquestrar fluxo de dados
- Redis
  - Cache
  - PubSub
- Client
  - Script python responsável por baixar arquivos do TSE
- Nginx
  - Serve os arquivos localmente
