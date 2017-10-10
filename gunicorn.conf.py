import multiprocessing, os

_s = os.environ.get('SERVICE', None)
_e = os.environ.get('ENVIRONMENT', 'staging')

if _s is None or _s == '':
    if os.path.exists('/repository'):
        _s = open('/repository', 'r').read().strip().split('/')[-1]
    else:
        _s = os.environ.get('HOSTNAME', 'unknown')

APP_NAME = '{0}.{1}'.format(_s, _e)
bool_map = {'':False, 'True': True, 'true': True, 'false': False, 'False': False}

bind = os.environ.get('GUNICORN_BIND', "0.0.0.0:80")

# the best setting so far was sync workers+threads
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
threads = int(os.environ.get('GUNICORN_THREADS', multiprocessing.cpu_count() * 4 + 1))

# restart aftex x reqs, 0 means no restart
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUEST_JITTER', 5))

timeout = int(os.environ.get('GUNICORN_TIMEOUT', 30))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 20))

preload_app = bool_map.get(os.environ.get('GUNICORN_PRELOAD_APP'), True)
chdir = os.path.dirname(__file__)
daemon = bool_map.get(os.environ.get('GUNICORN_DAEMON'), False)
debug = bool_map.get(os.environ.get('GUNICORN_DEBUG'), False)
loglevel=os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# The maximum number of pending connections (waiting to be served)
if worker_class == 'sync':
    backlog = max(workers * threads + 10, 100)
else:
    backlog = max(workers * (threads or 1) * 100, 1000)
    worker_connections = int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', 2*backlog))

access_log_format = '"%({X-Forwarded-For}i)s" "%(t)s" "%(r)s" "%(m)s" "%(U)s" "%(q)s" "%(H)s" "%(s)s" "%(b)s" "%(f)s" "%(a)s" "%(D)s" "%({cookie}i)s" "%({authorization}i)s"'

errorlog = '/tmp/%s.error.log' % APP_NAME
accesslog = '/tmp/%s.access.log' % APP_NAME
pidfile = '/tmp/gunicorn-%s.pid' % APP_NAME
