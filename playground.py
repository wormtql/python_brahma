from z3 import *

x = BitVec("x", 32)
y = BitVec("y", 32)
solver = Solver()

result = []
inputs = [x]
output = y

for i in range(32):
    temp = [Extract(i, i, inputs[0]) == 1]
    for j in range(0, i):
        temp.append(Extract(j, j, inputs[0]) == 0)
    temp2 = [Extract(i, i, output) == 0]
    for j in range(32):
        if j != i:
            temp2.append(Extract(j, j, output) == Extract(j, j, inputs[0]))
    result.append(Implies(And(temp), And(temp2)))

solver.add(result)
solver.add(x == 7)
print(solver.check())
print(solver.model())