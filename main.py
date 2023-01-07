from z3 import *
from solver import MySolver
from component import std_components


ctx = Context()
s = MySolver(component_function=std_components, ctx=ctx, bv=32)
s.solve(max_len=2)
