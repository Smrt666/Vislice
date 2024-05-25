from threading import Thread
from queue import Queue
from typing import Callable, Iterable, Optional, Any


def multirun(
    funcs: Iterable[Callable[[], None]],
    max_threads: int,
    print_progress: Optional[Callable[[Any], None]] = None,
) -> None:
    threads: Queue[Thread] = Queue()
    progress = 0
    for func in funcs:
        while threads.qsize() >= max_threads:
            thread = threads.get()
            thread.join()
            progress += 1

            if print_progress:
                print_progress(progress)

        thread = Thread(target=func)
        threads.put(thread)
        thread.start()

    while not threads.empty():
        thread = threads.get()
        thread.join()
        progress += 1
        if print_progress:
            print_progress(progress)
