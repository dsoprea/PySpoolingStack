import json
import pickle

from os.path import exists, basename
from os import makedirs, remove
from glob import glob
from collections import deque
from shutil import rmtree
from threading import Lock

from logging import getLogger
logging = getLogger(__name__)

_DefaultBundleSize = 500

_PickleTypes = { 'json':   (json.dump, json.load),
                 'pickle': (pickle.dump, pickle.load) }

class SStack(object):
    def __init__(self, path, bundle_size=_DefaultBundleSize, 
                 pickle_type='json', filename='stack'):
                 
        (self.__dump, self.__load) = _PickleTypes[pickle_type]

        self.__path        = path
        self.__bundle_size = bundle_size
        self.__pickle_type = pickle_type
        self.__filename    = filename
        self.__lock        = Lock()

        self.__deque      = None
        self.__min_bundle = None
        self.__max_bundle = None

        # Create a buffer to move our data through.
        self.__slice_buffer = range(self.__bundle_size)

    def __get_current_bundle_filepath(self):

        if self.__max_bundle == None:
            raise Exception("Can not get the current bundle filepath since no "
                            "bundles are available.")

        return ("%s/%s.%d" % (self.__path, self.__filename, \
                              self.__max_bundle))

    def __load_current_bundle(self):
        """Return the current bundle into our deque, and then remove the file.
        """

        bundle_filepath = self.__get_current_bundle_filepath()    

        logging.debug("Loading bundle from [%s]." % (bundle_filepath))

        with file(bundle_filepath, 'r') as f:
            for value in self.__load(f):
                self.__deque.append(value)

        remove(bundle_filepath)

    def __read_spool(self):
        """Load initial state."""

        # Safety.
        if self.__deque != None:
            return

        logging.debug("Reading spool directory [%s]." % (self.__path))
        
        if not exists(self.__path):
            makedirs(self.__path)

        filename_len = len(self.__filename)
        bundles = glob("%s/%s.*" % (self.__path, self.__filename))

        indices = []
        for filepath in bundles:
            filename = basename(filepath)
            indices.append(int(filename[filename_len + 1:]))

        indices = sorted(indices)

        self.__deque = deque()

        # Technically, min_bundle should always be 0, if there are any bundles. 
        # We don't wish to arbitrarily express this, though (no reason).
        self.__min_bundle   = indices[0]  if indices else -1
        self.__max_bundle   = indices[-1] if indices else -1

        logging.debug("Bundles read.  MIN= [%s]  MAX= [%s]" % 
                      (self.__min_bundle, self.__max_bundle))

    def reset(self):
        """Remove all data from the deque, and the filesystem."""

        logging.debug("Resetting spool at path [%s]." % (self.__path))

        self.__deque      = None
        self.__min_bundle = None
        self.__max_bundle = None

        try:
            rmtree(self.__path)
        except:
            pass
        
        if exists(self.__path):
            raise Exception("Spool path [%s] still exists after reset." % 
                            (self.__path))
        
    def __fill(self):
        """If there's at least one more unread bundle, read it in."""

        logging.debug("Checking for fillability.")

        if self.__max_bundle >= self.__min_bundle and self.__max_bundle != -1:
            self.__load_current_bundle()
            self.__max_bundle -= 1

    def __check_overflow(self):
        logging.debug("Spool has overflowed.")

        self.flush(self.__bundle_size)

    def flush(self, count=None, skip_on_error=True):
        """Move the last stored_bundle_size-number of values to file."""

        # Safety.
        if self.__deque == None:
            return

        deque_len = len(self.__deque)

        if count == None:
            count = deque_len
            
            if count == 0:
                return
        elif deque_len <= count:
            return

        logging.debug("Flushing with length (%d) and bundle-size (%d).  "
                      "MIN-BUNDLE= [%s]  MAX-BUNDLE= [%s]" % (deque_len, count, 
                      self.__min_bundle, self.__max_bundle))
        
        j = 0
        while j < count:
            value = self.__deque.popleft()
            self.__slice_buffer[j] = value

            j += 1

        self.__max_bundle += 1

        # If we're writing the first bundle in the collection.        
        if self.__max_bundle == 0:
            self.__min_bundle += 1
        
        bundle_filepath = self.__get_current_bundle_filepath()    
        with file(bundle_filepath, 'w') as f:
            try:
                self.__dump(self.__slice_buffer[0:count], f)
            except Exception as e:
                if not skip_on_error:
                    raise TypeError("Could not serialize one or more values "
                                    "to stack bundle [%s]: %s" % 
                                    (bundle_filepath, e))

        logging.debug("Bundle written to [%s] (%d)." % (bundle_filepath, len(self.__deque)))

    def __check_empty(self):
        """Make sure that the spool files have been read since loading. If we 
        don't have anything in our deque, attempt to fill it.
        """
    
        if self.__deque == None:
            self.__read_spool()
    
        if len(self.__deque) == 0:
            self.__fill()
        
    def pop(self):
        """Pop the last pushed value."""
    
        with self.__lock:
            self.__check_empty()

            try:    
                return self.__deque.pop()
            except IndexError:
                raise IndexError("Pop from empty SStack.")

    def push(self, value):
        """Add a new value."""

        with self.__lock:
            # Make sure that the spool path exists and that we have elements 
            # loaded, if possible.
            self.__check_empty()

            # Push it on the front.
            self.__deque.append(value)

            # Move the back bundle's worth of values to file.
            self.__check_overflow()

