from functools import lru_cache
from xmalplus import XmalPlus


@lru_cache
def get_xmal_model():
    return XmalPlus()
