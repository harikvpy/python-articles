# Python Generators - A Look Inside
<cite>Hari Mahadevan, hari@smallpearl.com</cite>

## Background
One of the most powerful features of Python is its `generator functions`. It also happens to be a feature that leads to confusion among its users; it can seem quite mysterious as to how generators do their magic. A decent understanding of how generators work inside the Python interpreter can be quite helpful in unraveling this mystery and should go some way in helping you write better code.

## Generator Functions
Before we get into the details of this article, it’s a good idea to recap what generator functions are and the best way to do that is by an example.

```
def my_range(start, end):
  # A function that mimics python’s standard range()
  index = start
  while index < end:
    yield index
    index += 1


for i in my_range(0, 10):
  print(i)
```

Nothing fancy about the code. It's just a limited implementation of Python’s standard function `range()`. A code example that has been extensively used in many Python books & articles. The magic happens when the interpreter encounters the keyword `yield`. During bytecode generation, this keyword tells the interpreter that the enclosing function is a generator function and it goes on to treat the function a little differently from a regular function. And this different treatment is what makes generator functions achieve its magic and it's this that is the topic of this article.

## Python Functions
Before we dig into the details of generators, it's necessary to have a basic understanding of how the Python interpreter executes the source code that we provide it. Specifically its functions.

A function in Python's interpreter has two distinct phases -- initialization and evaluation.

### Initialization
All functions in Python will have a corresponding frame object. Initialization is the phase where the interpreter creates this frame object. The frame object consists, among other things, of the following:

  - code object
  - stack
  - execution pointer
  - variables, local & global

You can imagine this as a C struct with a few appropriately named members for each of the above(and more). The `inspect` module documents this [here](https://docs.python.org/3/library/inspect.html#types-and-members).

When a function is initialized, a corresponding frame object is created. Arguments to the function are passed as `frame.f_local[arg1]`, `frame.f_locals['arg2']`, etc. As the function is executed, the instruction pointer to the function's bytecode is advanced via the `frame.f_lasti` member.


### Evaluation
Evaluation is actually a fancy way of saying *running* the function. And running the function involves passing the frame object created in the initialization phase to a function in the interpreter named [PyEval_EvalFrameDefault](https://github.com/python/cpython/blob/25104949a5a60ff86c10691e184ce2ecb500159b/Python/ceval.c#L880). If you look the linked source code, you can see that it's second parameter is `PyFrameObject* f`, the frame object that we're talking about.

The `PyEval_*` function takes the frame object passed to it and starts executing the function's bytecode pointed to by `frame.f_lasti`.

With this background we can go into generator functions and their functioning.

## Generator Functions

### Initialization
The initialization phase for generator functions is slightly different from a normal function. First of all, invoking a generator function does not result in its immediate execution. Rather a generator object is created. A frame object is still created, but it's stored as a member of the generator object. Specifically, its `gi_frame` member.

You can verify this by the following code (using the `my_range()` defined above) from the Python console:

```
>>> a = my_range(0, 5)
>>> type(a)
<class 'generator'>
>>> dir(a)
[..., 'close', 'gi_code', 'gi_frame', 'gi_running', 'gi_yieldfrom', 'send', 'throw']
```

### Evaluation
Evaluation or running of a generator function occurs when the builtin method `next()` is called with the generator object as its argument.

So using our original `my_range()` generator function:

```
>>> a = my_range(0, 5)
>>> next(a)
0
>>> next(a)
1
>>> next(a)
2
>>> next(a)
3
>>> next(a)
4
>>> next(a)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

What's going on here is that every time we call `next(a)`, it calls `PyEval_EvalFrameDefault` with the `generator.gi_frame` pointer. However, `PyEval_` *pauses* its execution when it encounters a `yield` statement. Note that I used the verb *pause* rather than *stop*. `PyEval_` returns placing the yielded value from the generator making it available for the callee. At this point it's important to note that the frame (`generator.gi_frame`), unlike regular functions, is not destroyed. Rather, it's preserved with its execution state. This allows Python to resume the frame when it's passed to `PyEval` via the subsequent call to `next()`.

The above cycle repeats until the generator function decides that it has reached its end of the yield iteration logic and returns. When this happens, `next()` generates a `StopIteration` exception. At this point the `gi_frame` held by the generator object can safely be destroyed.

## Generators in a for loop
In the real world we hardly use generator functions using the `next()` builtin. Instead we would iterate through the generator using a for loop. The for loop is actually a syntactic sugar on top of the `next()` and `StopIteration` exception, that presents a coding style similar to the traditional loop to the user. That is the for loop iterates through the generator's yielded values until `next()` throws a `StopIteration` exception.


## Communicating with generators

Generator functions also support other features such as allowing the callee to communicate with the generator function by sending it values. These are supported by methods `.send()` & `.throw()` which you can see in the output of `dir()`.

```
>>> import inspect
>>> inspect.getmembers(a)
[...., ('send', <built-in method send of generator object at 0x1053decf0>), ('throw', <built-in method throw of generator object at 0x1053decf0>)]
```

From an implementation point of view, `send()` pushes its argument to the top of the generator's stack and starts executing the generator's frame from the last paused state. This would cause a statement such as `a = yield x` to pop the argument to `send()` and place it as the value of the variable `a`. Similarly, `throw()` would transfer control back to the generator function's paused code, throwing the exception object passed as its argument.

## Conclusion
I hope the above discussion gives you a better idea of how Python generators are implemented by the interpreter that leads to its magic of continuously yielding values without having to complete its processing and store the result in a temporary local variable.

You can perceive a generator function as a closure as it preserves the function's execution pointer and its state, allowing it to be resumed. Come to think of it, this behavior is quite similar to threads in a multi-threaded environment. That is a *threading* system that doesn't require any support from the host CPU or the operating system. Of course one critical difference is that in a true multi-threaded system, threads are pre-emptively scheduled in and out. That doesn't happen here. Instead the *threads* (read, generator functions) have to yield control back to the callee for the function context switch to occur. This essentially is the behavior of a *cooperative multitasking* system. I'm not sure if anyone can remember this term -- remember Windows 3.x?!

This framework, of stopping & resuming functions is quite critical to implementing another powerful feature of the language. A feature that has become quite useful in achieving massive scaleability in this network-centric world. I'm talking about asynchronous programming, provided by the Python package `asyncio`. I hope to cover that in a follow-up article, contents of which will be easier to understand if you have a good grasp of the mechanisms discussed here.
