from z3 import *


class VarsLocation:
    def __init__(self, program_input_count, components, ctx):
        self.program_input_count = program_input_count
        self.components = components
        self.ctx = ctx

        self.program_input_location_vars = []
        for i in range(self.program_input_count):
            self.program_input_location_vars.append(Int(f"program_input_location_{i}", self.ctx))

        self.program_output_location_var = Int(f"program_output_location", self.ctx)

        self.input_location_vars = []
        self.output_location_vars = []
        for i in range(len(components)):
            component = components[i]
            input_count = component.get_input_count()
            self.input_location_vars.append([Int(f"input_location_var_{i}_{j}", self.ctx) for j in range(input_count)])
            self.output_location_vars.append(Int(f"output_location_var_{i}", self.ctx))

    def vars_flat(self):
        result = []
        for i in self.program_input_location_vars:
            result.append(i)
        result.append(self.program_output_location_var)
        for i in self.input_location_vars:
            for j in i:
                result.append(j)
        for i in self.output_location_vars:
            result.append(i)
        return result


class VarsIO:
    def __init__(self, program_input_count, components, ctx, it, bv):
        self.program_input_count = program_input_count
        self.components = components
        self.ctx = ctx
        self.it = it
        self.bv = bv

        self.program_input_vars = []
        for i in range(self.program_input_count):
            self.program_input_vars.append(BitVec(f"{it}_program_input_{i}", self.bv, self.ctx))

        self.program_output_var = BitVec(f"{it}_program_output", self.bv, self.ctx)

        self.input_vars = []
        self.output_vars = []
        for i in range(len(components)):
            component = components[i]
            input_count = component.get_input_count()
            self.input_vars.append([BitVec(f"{it}_input_var_{i}_{j}", self.bv, self.ctx) for j in range(input_count)])
            self.output_vars.append(BitVec(f"{it}_output_var_{i}", self.bv, self.ctx))