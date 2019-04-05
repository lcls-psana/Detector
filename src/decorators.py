#----------
"""
Page about how to generate class methods dynamically
  - https://stackoverflow.com/questions/8307602/programmatically-generate-methods-for-a-class

    @detector_list
    def raw(self, *args, **kwargs) : return self.raw(*args, **kwargs)

    # is equivalent to:
    def raw(self, *args, **kwargs) :
        return [o.raw(*args, **kwargs) for o in self.list_dets]
"""

#----------

import functools

def detector_list(f) :
    @functools.wraps(f)
    def wrapper_detector_list(self, *args, **kwargs) :
        return [f(o, *args, **kwargs) for o in self.list_dets]
    return wrapper_detector_list

#----------

#def add_method(cls, metname):
#    """also works: external to cls method to add prototyped methods to the class.
#    """
#    def _prototype(*args, **kwargs) :
#        return [getattr(o, metname)(*args, **kwargs) for o in cls.list_dets]
#   _prototype.__name__ = metname
#   setattr(cls, metname, _prototype)

#----------

#----------

def memorize(dic={}) :
    """Caching decorator
       E.g.: @memorize(); ...
    """
    def deco_memorize(f) :
        def wrapper(*args, **kwargs):
            fid = id(f)
            v = dic.get(fid, None)
            if v is None :
                v = dic[fid] = f(*args, **kwargs)
            return v
        return wrapper
    return deco_memorize

#----------

