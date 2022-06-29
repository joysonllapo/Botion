from datetime import datetime

def hello_job():
    print('Hello Job! The time is: %s' % datetime.now(), flush=True)