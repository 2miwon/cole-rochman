from kombu import Queue, Exchange

from cole_rochman.schedule import SCHEDULE

enable_utc = False

timezone = 'Asia/Seoul'

task_soft_time_limit = 60 * 2

# QUEUE SETTINGS
broker_transport_options = {
    'priority_steps': list(range(4)),  # 0: Very High / 1: High / 2: Middle / 3: Low
}

task_default_queue = 'default'
task_default_exchange_type = 'direct'
task_default_routing_key = 'default'

default_exchange = Exchange('default', type='direct')

task_queues = (
    Queue('default'),
)

beat_schedule = SCHEDULE
