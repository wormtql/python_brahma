from z3 import *


it = 0


def next_it():
    global it
    temp = it
    it += 1
    return temp


class Component:
    def __init__(self, name):
        self.name = name

    def semantic(self, inputs):
        raise "unimplemented"

    def get_input_count(self):
        raise "unimplemented"

    def parameters(self):
        return []

    def to_string(self, input_names, model):
        raise "unimplemented"

    def add_parameter_constraint(self, solver):
        pass


class ComponentConstant(Component):
    def __init__(self, ctx, bv):
        super().__init__("Const")
        self.ctx = ctx
        self.value = BitVec(f"const_{next_it()}", bv, ctx)

    def semantic(self, inputs):
        return self.value

    def get_input_count(self):
        return 0

    def parameters(self):
        return [self.value]

    def to_string(self, input_names, model):
        return f"Const {model.eval(self.value)}"


class ComponentAdd(Component):
    def __init__(self):
        super().__init__("Add")

    def semantic(self, inputs):
        return inputs[0] + inputs[1]

    def get_input_count(self):
        return 2

    def to_string(self, input_names, model):
        return f"Add {input_names[0]} {input_names[1]}"


class ComponentSub(Component):
    def __init__(self):
        super().__init__("Sub")

    def semantic(self, inputs):
        return inputs[0] - inputs[1]

    def get_input_count(self):
        return 2

    def to_string(self, input_names, model):
        return f"Sub {input_names[0]} {input_names[1]}"


class ComponentDec(Component):
    def __init__(self):
        super().__init__("Dec")

    def semantic(self, inputs):
        return inputs[0] - 1

    def get_input_count(self):
        return 1

    def to_string(self, input_names, model):
        return f"Dec {input_names[0]}"


class ComponentInc(Component):
    def __init__(self):
        super().__init__("Inc")

    def semantic(self, inputs):
        return inputs[0] + 1

    def get_input_count(self):
        return 1

    def to_string(self, input_names, model):
        return f"Inc {input_names[0]}"


class ComponentBitAnd(Component):
    def __init__(self):
        super().__init__("BitAnd")

    def semantic(self, inputs):
        return inputs[0] & inputs[1]

    def get_input_count(self):
        return 2

    def to_string(self, input_names, model):
        return f"And {input_names[0]} {input_names[1]}"


class ComponentBitOr(Component):
    def __init__(self):
        super().__init__("BitOr")

    def semantic(self, inputs):
        return inputs[0] | inputs[1]

    def get_input_count(self):
        return 2

    def to_string(self, input_names, model):
        return f"Or {input_names[0]} {input_names[1]}"


class ComponentBitXor(Component):
    def __init__(self):
        super().__init__("BitXor")

    def semantic(self, inputs):
        return inputs[0] ^ inputs[1]

    def get_input_count(self):
        return 2

    def to_string(self, input_names, model):
        return f"Xor {input_names[0]} {input_names[1]}"


# 左移常数位
class ComponentLSL(Component):
    def __init__(self, ctx, bv):
        super().__init__("LSL")
        self.ctx = ctx
        self.bv = bv
        self.value = BitVec(f"lsl_{next_it()}", bv, ctx=ctx)

    def semantic(self, inputs):
        return inputs[0] << self.value

    def get_input_count(self):
        return 1

    def parameters(self):
        return self.value,

    def to_string(self, input_names, model):
        return f"LSL {input_names[0]} {model.eval(self.value)}"

    def add_parameter_constraint(self, solver):
        solver.add(self.value >= 1)
        solver.add(self.value <= 32)


class ComponentNeg(Component):
    def __init__(self):
        super().__init__("NEG")

    def semantic(self, inputs):
        return -inputs[0]

    def get_input_count(self):
        return 1

    def to_string(self, input_names, model):
        return f"NEG {input_names[0]}"


def std_components(ctx, bv):
    return [
        ComponentAdd(),
        ComponentAdd(),
        ComponentSub(),
        ComponentInc(),
        ComponentDec(),
        ComponentBitAnd(),
        ComponentBitOr(),
        ComponentBitXor(),
        ComponentLSL(ctx, bv),
        # ComponentNeg(),
        # ComponentConstant(ctx, bv),
    ]
