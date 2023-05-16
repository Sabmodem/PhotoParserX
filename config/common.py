import os

searx_url = 'http://searx:8080'
# searx_url = 'http://localhost:8888'
log_dir = os.path.join(os.getcwd(), 'log')
img_dir = os.path.join(os.getcwd(), 'img')
archives_dir = os.path.join(os.getcwd(), 'static', 'archives')

# web app config
wsgi_port = 8000
wsgi_listen_addr = '0.0.0.0'
wsgi_url = f'http://127.0.0.1:{wsgi_port}'
bind = f'{wsgi_listen_addr}:{wsgi_port}'
history_items_per_page = 10
results_per_page = 50

# websocker server config
ws_port = 8765
ws_listen_addr = '0.0.0.0'
ws_url = f'ws://127.0.0.1:{ws_port}'

# rq config
redis_host = 'redis'
# redis_host = 'localhost'
redis_port = 6379
search_task_timeout = 3600
download_task_timeout = 3600

dict_config = {var: globals()[var] for var in [var for var in dir() if var[0:2] != '__']}
