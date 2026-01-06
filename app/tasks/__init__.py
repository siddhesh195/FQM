import os

from app.utils import find
from app.tasks.cache_tickets_tts import CacheTicketsAnnouncements
from app.tasks.delete_tickets import DeleteTickets
from flask import current_app


THREADS = {}
TASKS = [CacheTicketsAnnouncements, DeleteTickets]


def materialize_tasks(app, tasks=TASKS):
    app = app or current_app
    

    for task in tasks:
        if task.__name__ in THREADS:
            continue

        task_obj = task(app)
        if task_obj.settings.enabled:
            THREADS[task.__name__] = task_obj

    return THREADS


def start_task_threads():
    for task in THREADS.values():
        if task.settings.enabled and not task.dead:
            task.init()



def start_tasks(app=None, tasks=TASKS):
    """
    Compatibility wrapper.
    Prefer materialize_tasks() + start_task_threads().
    """
    app = app or current_app

    # 🚨 DO NOT start threads in tests
    if app.config.get("TESTING", False):
        materialize_tasks(app, tasks)
        return THREADS

    if app.config.get("MIGRATION") or os.environ.get("DOCKER"):
        return THREADS

    materialize_tasks(app, tasks)
    start_task_threads()

    return THREADS


def stop_tasks(tasks=[]):
    ''' stop all tasks in `tasks or TASKS`.

    Parameters
    ----------
        tasks: list
            list of task names to stop, if empty will stop all.
    '''
    threads = [i for i in THREADS.items() if i[0] in tasks]\
        if tasks else list(THREADS.items())

    for task, thread in threads:
        if not thread.quiet:
            print(f'Stopping task: {task} ...')

        thread.stop()
        THREADS.pop(task)


def get_task(task_name):
    ''' get a task if running.

    Parameters
    ----------
    task_name : str
        task name to find in list of running tasks.
    '''
    item = find(lambda i: i[0] == task_name, THREADS.items())

    return item and item[1]
