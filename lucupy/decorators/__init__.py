# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import numpy as np


def scalar_input(func):
    """
    Decorator to convert a function that returns a tuple to a function that returns a scalar.
    TODO: This is not currently being used. Ultimately, we would add it to the functions in the sky package.
    TODO: TO IMPLEMENT THIS IS NECESSARY TO REMOVE ASTROPY outputs or make them numpy compatible.
    """

    def wrapper(*args, **kwargs):
        # transform the input to numpy
        np_args = [np.asarray(arg) for arg in args]
        if any(arg.ndim == 0 for arg in np_args):
            args = [arg[np.newaxis] for arg in np_args]

        return np.squeeze(func(*args, **kwargs))

    return wrapper


def immutable(cls):
    """
    This marks a class as being immutable, i.e., when doing a copy or a deep copy, we only return self
    instead of actually making a copy of the class. It should only be used in dataclasses that are marked frozen.

    It works by implementing the __deepcopy__ and __copy__ dunder methods.
    """
    def __deepcopy__(self, _):
        return self

    def __copy__(self):
        return self

    setattr(cls, '__deepcopy__', __deepcopy__)
    setattr(cls, '__copy__', __copy__)
    return cls
