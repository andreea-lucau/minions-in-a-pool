"""This is an example of using a thread pool to solve several tasks."""
#!/usr/bin/env python
# pylint: disable=star-args
import argparse
import datetime
import logging
import os
import Queue
import random
import sys
import threading
import time


class Minion(threading.Thread):
    """A worker minion - it gets tasks for the thread pool and executes them."""

    def __init__(self, minion_id, tasks):
        threading.Thread.__init__(self)

        self.minion_id = minion_id
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                logging.info(
                    "[%d] Executing %s(%s, %s)",
                    self.minion_id, func.__name__, args, kwargs)
                func(*args, **kwargs)
            # pylint: disable=broad-except
            except Exception as ex:
                logging.error(
                    "[%d] Error executing %s(%s, %s): %s",
                    self.minion_id, func.__name__, args, kwargs, ex)
            self.tasks.task_done()


class MinionsPool(object):
    """A thread pool - it sets up workers and gives them tasks."""

    def __init__(self, size):
        self.tasks = Queue.Queue(size)
        for i in range(size):
            Minion(i, self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


def busy_work(delay):
    """Sample task - just sleeps

    Args:
        delay: int, how much to sleep
    """
    time.sleep(delay)


def work_my_minions(pool_size, task_no):
    """Creates a thread pool and gives it tasks to run.

    Args:
        pool_size: int, how many minions are in the pool
        task_no: int, how many tasks will they execute
    """
    logging.info("Will create a pool of size %d to solve %d tasks",
                 pool_size, task_no)

    pool = MinionsPool(pool_size)
    total_delay = 0
    start = time.time()

    for _ in range(task_no):
        delay = random.randrange(1, 10)
        total_delay += delay
        pool.add_task(busy_work, delay)

    pool.wait_completion()
    end = time.time()

    logging.info(
        "All work is done. Total delay: %d, actual delay: %d",
        total_delay, end - start
    )


def parse_argv():
    """Parse command line arguments.

    The script accepts:
        --pool_size - how many workers will execute the tasks
        --task_no - how many tasks will they have to execute
        --log_dir - optional, the directory where to save logs

    Returns:
        pool_size, task_no, log_dir
    """
    parser = argparse.ArgumentParser(
        description="Do minion <task_no> tasks in a pool of "
                    "<pool_size> thread pool.")

    parser.add_argument(
        "--pool_size", metavar="pool_size", type=int, required=True,
        help="How many minion threads will work on the tasks")

    parser.add_argument(
        "--task_no", metavar="task_no", type=int, required=True,
        help="How many tasks to execute")

    parser.add_argument(
        "--log_dir", metavar="log_dir", type=str, default=None, required=False,
        help="The directory used for storing logs. "
             "If not set, will log to stderr")

    args = parser.parse_args()

    return args.pool_size, args.task_no, args.log_dir


def setup_logging(log_dir, level=logging.INFO):
    """Setup the log file/stream

    Args:
        log_dir: string or None - if string, will log to
            log_dir/minion_<date>.log, otherwise will log to stdout
        level: optional, logging level. The default value is INFO
    """
    logging_config = dict(
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%I:%M:%S %p",
        level=level
    )

    if log_dir:
        now = datetime.datetime.now()
        log_filename = os.path.join(
            log_dir, "minions_%s_.log" % now.strftime("%d_%m_%y"),
        )
        logging.basicConfig(filename=log_filename, **logging_config)
    else:
        logging.basicConfig(stream=sys.stdout, **logging_config)


if __name__ == "__main__":
    POOL_SIZE, TASK_NO, LOG_DIR = parse_argv()
    setup_logging(LOG_DIR)
    work_my_minions(POOL_SIZE, TASK_NO)
