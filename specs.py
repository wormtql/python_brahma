from z3 import *


def spec_turn_off_rightmost_bit(inputs, output, bv):
    result = []

    for i in range(bv):
        temp = [Extract(i, i, inputs[0]) == 1]
        for j in range(0, i):
            temp.append(Extract(j, j, inputs[0]) == 0)
        temp2 = [Extract(i, i, output) == 0]
        for j in range(bv):
            if j != i:
                temp2.append(Extract(j, j, output) == Extract(j, j, inputs[0]))
        result.append(Implies(And(temp), And(temp2)))
    return result


def spec_left_shift_n(inputs, output, n):
    result = []
    result.append(output == inputs[0] << n)
    return result
