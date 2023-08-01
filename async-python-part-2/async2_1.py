import random
import types
from collections import deque
from time import sleep

def wait_for_io_result():
    sleep(random.random()/2)

@types.coroutine
def task1_part1():
    print("task1_part1.1")
    wait_for_io_result()
    yield
    print("task1_part1.2")
    wait_for_io_result()
    yield

def task1_part2():
    print("task1_part2.0")
    wait_for_io_result()
    yield
    print("task1_part2.1")
    wait_for_io_result()
    yield
    print("task1_part2.2")
    wait_for_io_result()
    yield

def task1_part3():
    print("task1_part3.1")
    wait_for_io_result()
    yield
    print("task1_part3.2")
    wait_for_io_result()
    yield
    print("task1_part3.3")
    wait_for_io_result()
    yield
    print("task1_part3.4")
    wait_for_io_result()
    yield
    print("task1_part3.5")
    wait_for_io_result()
    yield

def task1_part4():
    yield from task1_part1()

class MyConcurrentRunner:
    def __init__(self) -> None:
        self.tasks = deque([])

    def create_task(self, coro):
        self.tasks.append(coro)

    def run(self):
        while self.tasks:
            next_task = self.tasks.popleft()
            while True:
                try:
                    next(next_task)
                except StopIteration:
                    break


if __name__ == '__main__':
    runner = MyConcurrentRunner()
    runner.create_task(task1_part1())
    runner.create_task(task1_part2())
    runner.create_task(task1_part3())
    runner.create_task(task1_part4())
    runner.run()
