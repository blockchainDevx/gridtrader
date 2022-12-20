# -*- coding: utf-8 -*-

import threading
from concurrent.futures import ThreadPoolExecutor

threadPoolExecutor = None


def init_thread_pool_executor(max_workers=None, thread_name_prefix=''):
    global threadPoolExecutor
    threadPoolExecutor = ThreadPoolExecutor(max_workers, thread_name_prefix)