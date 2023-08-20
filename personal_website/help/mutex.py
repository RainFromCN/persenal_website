from threading import Semaphore, Lock

cooperation_locks_mutex = Lock()
cooperation_locks = {}


def _get_cooperation_lock(cid):
    cid = int(cid)
    cooperation_locks_mutex.acquire()
    if cid not in cooperation_locks:
        cooperation_locks[cid] = Lock()
    cooperation_locks_mutex.release()
    return cooperation_locks[cid]