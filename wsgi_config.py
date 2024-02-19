import os
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(ROOT_PATH, 'log')

bind = '0.0.0.0:5000'
worker_class = 'gevent'
workers = 2
daemon = False
reload = True
pidfile = os.path.join(ROOT_PATH, "gunicorn.pid")  # Gunicorn  pid的位置
loglevel = 'info'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = os.path.join(LOG_PATH, "gunicorn_access.log")
errorlog = os.path.join(LOG_PATH, "gunicorn_error.log")
