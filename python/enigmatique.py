#!/usr/bin/python3.7

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import yaml
import redis as redis_lib

version = "0.1"

with open('enigmatique.yaml') as config_file:
    cfg = yaml.safe_load(config_file)
REDIS_HOST = cfg['redis']['host']
REDIS_PORT = cfg['redis']['port']
REDIS_PASSWORD = cfg['redis']['password']
REDIS_DB = cfg['redis']['db']
EXPORTER = cfg['exporter']['port']

if REDIS_PASSWORD == "null":
    redis = redis_lib.Redis(host=REDIS_HOST,
                            port=REDIS_PORT,
                            db=REDIS_DB)
else:
    redis = redis_lib.Redis(host=REDIS_HOST,
                            port=REDIS_PORT,
                            db=REDIS_DB,
                            password=REDIS_PASSWORD)

def build_metrics():
    global t
    metrics = []
    prom = []
    for k in redis.keys('enigmatique*type'):
        metrics.append(k.decode('utf-8').split(':')[0])
    for metric in metrics:
        m_hlp = ':'.join([metric,'help'])
        m_hlp_val = redis.get(m_hlp)
        hlp = ''.join(['# HELP ',metric, ' ', m_hlp_val.decode('utf-8')])
        prom.append(hlp)
        m_type = redis.get(':'.join([metric,'type']))
        if m_type.decode('utf-8') == 'c':
            t = 'counter'
        if m_type.decode('utf-8') == 'g':
            t = 'gauge'
        prom.append(''.join(['# TYPE ', metric, ' ', t]))
        num_values = redis.keys(':'.join([metric,'value*']))
        if len(num_values) == 1:
            m_value = redis.get(':'.join([metric,'value','0']))
            prom.append(' '.join([metric,m_value.decode('utf-8')]))
        else:
            m_keys = sorted(redis.keys(':'.join([metric, 'value*'])))
            for key in m_keys:
                key_label = key.decode().split(':')[2]
                label = ''.join(['{','label=','"',key_label,'"','}'])
                prom.append(''.join([metric,label,' ',redis.get(key).decode('utf-8')]))

class ThreadedHTTPServer(HTTPServer, ThreadingMixIn):
    pass

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == '/metrics':
            try:
                build_metrics()
                self.send_response(200)
                self.send_header('Enigmatique',f'{version}')
                self.end_headers()
                self.wfile.write('\n'.join(prom).encode())
                self.wfile.write('\n'.encode())
            except:
                self.send_response(500)
                self.send_header('Enigmatique',f'{version}')
                self.end_headers()
                self.wfile.write('Error getting metrics\n'.encode())
        else:
            self.send_response(404)
            self.end_headers()

httpd = ThreadedHTTPServer(('0.0.0.0', EXPORTER), SimpleHTTPRequestHandler)
httpd.serve_forever()
