from vars import VarsLocation, VarsIO
from component import ComponentConstant

class Program:
    def __init__(self, location_vars: VarsLocation, model, components, program_input_count):
        self.locations_vars = location_vars
        self.components = components
        self.program_input_count = program_input_count
        self.model = model

    def to_program_string(self):
        p = []
        for i in range(self.program_input_count):
            p.append(f"a{i} = INPUT{i}")

        instructions = []
        for i in range(len(self.components)):
            loc = self.model.eval(self.locations_vars.output_location_vars[i]).as_long()
            inputs = []
            for j in self.locations_vars.input_location_vars[i]:
                inputs.append(self.model.eval(j).as_long())
            instructions.append((self.components[i], loc, inputs, i))

        instructions = sorted(instructions, key=lambda x: x[1])

        output_location = self.model.eval(self.locations_vars.program_output_location_var).as_long()
        for i in range(output_location - self.program_input_count + 1):
            (component, loc, inputs, index) = instructions[i]
            input_names = [f"a{i}" for i in inputs]
            line = component.to_string(input_names, self.model)
            p.append(f"a{i + self.program_input_count} = {line}")
            # p.append(f"a{i + self.program_input_count} = {component.name} {['a' + str(j) for j in inputs]}")

        return "\n".join(p)
