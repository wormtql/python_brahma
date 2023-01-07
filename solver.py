from z3 import *
from component import *
import random
from vars import VarsIO, VarsLocation
from program import Program
from typing import Tuple, List, Union
from specs import *


def random_bitvec(bv):
    max_value = (1 << bv) - 1
    return random.randint(0, max_value)


def constraint_program_inout_location(vars: VarsLocation, program_input_count: int, component_size: int):
    result = []
    for i in range(program_input_count):
        result.append(vars.program_input_location_vars[i] == i)

    # program output location can be used to constraint program size
    # result.append(vars.program_output_location_var == self.program_input_count + len(self.components) - 1)
    result.append(vars.program_output_location_var >= 0)
    result.append(vars.program_output_location_var <= program_input_count + component_size - 1)
    return result


def acyclicity_constraint(vars: VarsLocation, component_size: int):
    result = []
    for i in range(component_size):
        input_count = len(vars.input_location_vars[i])
        for j in range(input_count):
            result.append(vars.input_location_vars[i][j] < vars.output_location_vars[i])
    return result


def consistency_constraint(vars: VarsLocation, component_size: int):
    result = []
    for i in range(component_size):
        for j in range(i + 1, component_size):
            result.append(vars.output_location_vars[i] != vars.output_location_vars[j])
    return result


def connectivity_constraint(vars_io: VarsIO, vars_location: VarsLocation):
    result = []
    location_list = []
    for i in vars_location.program_input_location_vars:
        location_list.append(i)
    location_list.append(vars_location.program_output_location_var)
    for i in vars_location.input_location_vars:
        for j in i:
            location_list.append(j)
    for i in vars_location.output_location_vars:
        location_list.append(i)

    value_list = []
    for i in vars_io.program_input_vars:
        value_list.append(i)
    value_list.append(vars_io.program_output_var)
    for i in vars_io.input_vars:
        for j in i:
            value_list.append(j)
    for i in vars_io.output_vars:
        value_list.append(i)

    n = len(location_list)
    assert(n == len(value_list))
    for i in range(n):
        for j in range(i + 1, n):
            result.append(Implies(location_list[i] == location_list[j], value_list[i] == value_list[j]))
    return result


def well_formed_program_constraint(vars: VarsLocation, program_input_count: int, component_size: int):
    result = []
    m = program_input_count + component_size

    # constraint for input locations
    for i in range(component_size):
        for j in vars.input_location_vars[i]:
            result.append(0 <= j)
            result.append(j <= m - 1)

    # constraint for output locations
    for i in vars.output_location_vars:
        result.append(program_input_count <= i)
        result.append(i <= m - 1)

    # constraint for program input locations, which is constant
    result += constraint_program_inout_location(vars, program_input_count, component_size)

    # cons
    result += consistency_constraint(vars, component_size)

    # acyc
    result += acyclicity_constraint(vars, component_size)
    return result


def lib_constraint(vars: VarsIO, components):
    result = []
    component_size = len(components)
    for i in range(component_size):
        component = components[i]
        result.append(vars.output_vars[i] == component.semantic(vars.input_vars[i]))
    return result


class MySolver:
    def __init__(self, component_function, ctx, bv):
        self.ctx = ctx
        self.synthesizer = Solver(ctx=self.ctx)
        self.components: List[Component] = component_function(ctx, bv)
        self.bv = bv
        self.component_size = len(self.components)
        self.component_function = component_function
        self.program_input_count = 2

    def solve(self, max_len=None):
        counter_examples = [[random_bitvec(self.bv) for _ in range(self.program_input_count)]]
        # counter_examples = [[587666393, 2735734657]]
        example_output = [self.spec(counter_examples[0])]
        # example_output = [587666392]
        all_io_vars = [VarsIO(self.program_input_count, self.components, self.ctx, 0, self.bv)]
        location_vars = VarsLocation(self.program_input_count, self.components, self.ctx)

        if max_len is not None:
            self.synthesizer.add(location_vars.program_output_location_var <= self.program_input_count + max_len - 1)

        self.synthesizer.add(well_formed_program_constraint(location_vars, self.program_input_count, self.component_size))
        for c in self.components:
            c.add_parameter_constraint(self.synthesizer)

        while True:
            print(counter_examples[-1], example_output[-1])
            # add the last counter-example, because the former is already added in previous iteration
            self.synthesizer.add(lib_constraint(all_io_vars[-1], self.components))
            self.synthesizer.add(connectivity_constraint(all_io_vars[-1], location_vars))
            self.synthesizer.add(self.spec_constraint(all_io_vars[-1].program_input_vars, all_io_vars[-1].program_output_var))
            # set program inputs/outputs to counter examples
            for i in range(self.program_input_count):
                self.synthesizer.add(all_io_vars[-1].program_input_vars[i] == counter_examples[-1][i])
            self.synthesizer.add(all_io_vars[-1].program_output_var == example_output[-1])

            syn_result = self.synthesizer.check()
            print(syn_result)
            model = None
            program = None
            if syn_result == sat:
                model = self.synthesizer.model()
                # print(self.synthesizer.model())
                program = Program(location_vars, model, self.components, self.program_input_count)
                print(program.to_program_string())
            else:
                return None

            verify_result = self.verify(location_vars, model)
            if verify_result is None:
                return program
            else:
                counter_examples.append(verify_result)
                output = self.spec(verify_result)
                example_output.append(output)
                all_io_vars.append(VarsIO(self.program_input_count, self.components, self.ctx, len(all_io_vars), self.bv))

    def verify(self, location_vars, model):
        new_ctx = Context()
        verifier = Solver(ctx=new_ctx)

        location_vars2 = VarsLocation(self.program_input_count, self.components, new_ctx)
        locations_vars_flat = location_vars.vars_flat()
        locations_vars2_flat = location_vars2.vars_flat()
        for i in range(len(locations_vars2_flat)):
            val = model.eval(locations_vars_flat[i]).as_long()
            verifier.add(locations_vars2_flat[i] == val)

        verity_components: List[Component] = self.component_function(new_ctx, self.bv)
        component_parameters = []
        for c in verity_components:
            for item in c.parameters():
                component_parameters.append(item)
        component_parameters2 = []
        for c in self.components:
            for item in c.parameters():
                component_parameters2.append(item)
        for i in range(len(component_parameters)):
            val = model.eval(component_parameters2[i]).as_long()
            verifier.add(component_parameters[i] == val)

        io_vars = VarsIO(self.program_input_count, self.components, new_ctx, 0, self.bv)

        verifier.add(connectivity_constraint(io_vars, location_vars2))
        verifier.add(lib_constraint(io_vars, verity_components))
        verifier.add(Not(And(self.spec_constraint(io_vars.program_input_vars, io_vars.program_output_var))))
        result = verifier.check()
        if result == sat:
            model = verifier.model()
            inputs = []
            for i in io_vars.program_input_vars:
                # because some inputs might not be used, so the verifier's model will not contain that variable
                inputs.append(model.eval(i, True).as_long())
            return inputs
        else:
            return None

    def spec(self, inputs):
        vs = []
        new_ctx = Context()
        solver = Solver(ctx=new_ctx)

        for i in range(len(inputs)):
            v = BitVec(f"input{i}", self.bv, new_ctx)
            vs.append(v)
            solver.add(v == inputs[i])

        output = BitVec("output", self.bv, new_ctx)
        solver.add(self.spec_constraint(vs, output))
        solver.check()
        model = solver.model()
        return model.eval(output).as_long()

    def spec_constraint(self, inputs, output):
        # result = []
        #
        # for i in range(self.bv):
        #     temp = [Extract(i, i, inputs[0]) == 1]
        #     for j in range(0, i):
        #         temp.append(Extract(j, j, inputs[0]) == 0)
        #     temp2 = [Extract(i, i, output) == 0]
        #     for j in range(self.bv):
        #         if j != i:
        #             temp2.append(Extract(j, j, output) == Extract(j, j, inputs[0]))
        #     result.append(Implies(And(temp), And(temp2)))
        # return result
        # return spec_left_shift_n(inputs, output, n=10)
        # return [output == inputs[0] & 0x1111]
        # return [output == 2 * inputs[0] + 3 * inputs[1]]
        return spec_turn_off_rightmost_bit(inputs, output, self.bv)

