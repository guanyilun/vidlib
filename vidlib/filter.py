import numpy as np

_search_fields = ['submobjects', 'mobjects']

def find_by_type(mob, typ, recursive=False):
    res = []
    if isinstance(mob, typ):
        return [mob]
    elif isinstance(mob, list):
        for m in mob:
            res += find_by_type(m, typ, recursive=recursive)
        return res
    elif recursive:
        mobs = [getattr(mob, field) for field in _search_fields if hasattr(mob, field)]
        if len(mobs) == 0: return []
        else:
            mobs = [mob for sublist in mobs for mob in sublist]  # flatten
            return find_by_type(mobs, typ, recursive=recursive)
    else: return res

def find_by_field(mobs, field, value):
    res = []
    if isinstance(mobs, list):
        for mob in mobs:
            res += find_by_field(mob, field, value)
        return res
    else:
        if hasattr(mobs, field) and \
           (getattr(mobs, field) == value or value in getattr(mobs, field)):
            return [mobs]
        else:
            return []
