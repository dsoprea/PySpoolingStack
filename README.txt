PySpoolingStack
===============

A stack that will only grow to a certain point before it pushes to physical 
files, and vice-versa.

Example
=======

Implementing the "spooling stack" (SStack):

    >>> from pyspoolingstack.sstack import SStack
    >>> from pyspoolingstack.sstackcollection import SStackCollection

    >>> stack1 = SStack('/tmp/stack1')
    >>> stack1.push('aa')
    >>> stack1.push('bb')
    >>> stack1.push('cc')
    >>> stack1.flush()

    >>> collect1 = SStackCollection('/tmp/collect1')
    >>> stack2 = collect1.build_stack('stack2')
    >>> stack2.push('dd')
    >>> stack2.push('ee')
    >>> stack2.push('ff')
    >>> stack3 = collect1.build_stack('stack3')
    >>> stack3.push('gg')
    >>> stack3.push('hh')
    >>> stack3.push('ii')
    >>> collect1.flush()

The existing spools are automatically loaded if available:

    >>> collect1 = SStackCollection('/tmp/collect1')
    >>> stack2 = collect1.build_stack('stack2')
    >>> stack2.pop()
    u'ff'
    >>> stack2.pop()
    u'ee'
    >>> stack2.pop()
    u'dd'
    >>> stack2.pop()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyspoolingstack/sstack.py", line 182, in pop
        raise IndexError("Pop from empty SStack.")
    IndexError: Pop from empty SStack.
    >>> 

The physical files are bundles of JSON, which are reasonably (and configurably) 
sized:

    $ ls -l /tmp/stack1/
    total 4
    -rw-rw-r-- 1 dustin dustin 18 Jan 18 02:31 stack.0

    $ ls -l /tmp/collect1/
    total 8
    drwxrwxr-x 2 dustin dustin 4096 Jan 18 02:32 stack2
    drwxrwxr-x 2 dustin dustin 4096 Jan 18 02:32 stack3

    $ ls -l /tmp/collect1/stack2
    total 4
    -rw-rw-r-- 1 dustin dustin 18 Jan 18 02:32 stack.0

    $ ls -l /tmp/collect1/stack3
    total 4
    -rw-rw-r-- 1 dustin dustin 18 Jan 18 02:32 stack.0

    $ cat /tmp/collect1/stack3/stack.0 
    ["gg", "hh", "ii"]$ 

Comments
========

Always make sure to flush, or lose whatever is not currently saved to disk.


