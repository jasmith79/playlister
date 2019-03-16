"""
.. py:module:: playlister_utils
    :platform: Unix, Windows
    :synopsis: Generic utility functions for the playlister utility.
"""

from functools import partial
from unicodedata import normalize as uni_norm
from typing import Callable, Any, List

# convert combining diacritical marks to combined form
normalize = partial(uni_norm, "NFC")


def pipe(*fs: Callable[..., Any]) -> Callable[..., Any]:
    """Forward function composition. Yes, I know mutation is evil.
        First function may be of any arity, all others must be unary.

        :param fs: the function arguments, gathered into a list.
        :returns: a function that pipes the passed argument through
            the functions in order.
    """
    def collect(*args, **kwargs):
        head, *tail = fs
        result = head(*args, **kwargs)
        for f in tail:
            result = f(result)
        return result
    return collect