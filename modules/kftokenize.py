"""Tokenization for plagiarism checking.
"""

import collections
import functools
import itertools
import re
from kftoken import *

import kftoken
__all__ = kftoken.__all__ + []
del kftoken

# memorize function into cache (expression is compiled as unicode)
@functools.lru_cache
def _compile(expr):
    return re.compile(expr, re.UNICODE)

class TokenNode(collections.namedtuple('TokenNode', 'type string start end line')):
    def __repr__(self):
        annotated_type = '%d (%s)' % (self.type, names[self.type])
        return ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))

# regex group functions (grouping with or)
def group(*choices): return '(' + '|'.join(choices) + ')'
def any(*choices): return group(*choices) + '*'
def maybe(*choices): return group(*choices) + '?'

# making regex for every number literal
Hexnumber = r'0[xX](?:_?[0-9a-fA-F])+'
Binnumber = r'0[bB](?:_?[01])+'
Octnumber = r'0[oO](?:_?[0-7])+'
Decnumber = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat = group(r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?', r'\.[0-9](?:_?[0-9])*') + maybe(Exponent)
Expfloat = r'[0-9](?:_?[0-9])*' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r'[0-9](?:_?[0-9])*[jJ]', Floatnumber + r'[jJ]')
# combine all number regexes into single regex
Number = group(Imagnumber, Floatnumber, Intnumber)

# generate prefixes used in python
def _all_string_prefixes():
    _valid_string_prefixes = ['b', 'r', 'u', 'f', 'br', 'fr']
    result = {''}
    for prefix in _valid_string_prefixes:
        for perm in itertools.permutations(prefix):
            for prod in itertools.product(*[(pref, pref.upper()) for pref in perm]):
                result.add(''.join(prod))
    return result

StringPrefix = group(*_all_string_prefixes())
