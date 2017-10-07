from parsy import generate, match_item, test_item


class Command:
    def __init__(self, parameter):
        self.parameter = parameter

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.parameter)


class Forward(Command):
    pass


class Backward(Command):
    pass


class Right(Command):
    pass


class Left(Command):
    pass


commands = {
    'fd': Forward,
    'bk': Backward,
    'rt': Right,
    'lt': Left,
}


@generate
def statement():
    cmd_name = yield test_item(lambda i: i in commands.keys(), "command")
    parameter = yield test_item(lambda i: isinstance(i, int), "number")
    yield match_item('\n')
    return commands[cmd_name](int(parameter))


program = statement.many()
