from pyspoolingstack.sstack import SStack

class SStackCollection(object):
    """A general collection of many stacks. This makes it more intuitive to 
    create several stacks to push data to in parallel, as well as providing a 
    single call to flush all of them.
    """

    def __init__(self, collection_path):
        self.__collection_path = collection_path
        self.__stacks = {}

    def build_stack(self, name, *args, **kwargs):
        """Build a new stack object, and keep track of it."""
    
        stack_path = ("%s/%s" % (self.__collection_path, name))
        
        stack = SStack(stack_path, *args, **kwargs)
        self.__stacks[name] = stack
        
        return stack

    def get_stack(self, name):
        """Return a previously-built stack object."""

        return self.__stacks[name]

    def flush(self):
        """Flush all stacks."""
    
        for name, stack in self.__stacks.iteritems():
            stack.flush()

    def reset(self):
        """Flush all stacks."""
    
        for name, stack in self.__stacks.iteritems():
            stack.reset()

