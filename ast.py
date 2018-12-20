reservedWords = ('define', 'if', 'while', 'begin', 'set')
builtIns = ('+', '-', '*', '/', '=', '<', '>',
    'cons', 'car', 'cdr', 'number?', 'symbol?', 'list?', 'null?',
    'print')

class Environment:
    def __init__(self, values, enclosed):
        self.values = values
        self.enclosed = enclosed

class Exp: pass

# value expression
class ValExp(Exp):
    def __init__(self, sxp):
        self.sxp = sxp

    def __str__(self):
        return str(self.sxp)

    def __repr__(self):
        s = 'ValExp(' + repr(self.sxp) + ')'
        return s

# a lambda function
class Lambda(Exp):
    def __init__(self, formals, body):
        self.formals = formals
        self.body = body

    def __str__(self):
        s = '(lambda ('
        s += ' '.join([ str(elt) for elt in self.formals ])
        s += ') '
        s += str(self.body)
        s += ')'
        return s

    def __repr__(self):
        s = 'Lambda(['
        s += ', '.join([ repr(elt) for elt in self.formals ])
        s += '], ' + repr(self.body) + ')'
        return s

# variable expression
class VarExp(Exp):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        s = 'VarExp(' + repr(self.name) + ')'
        return s

# applicative expression
class ApExp(Exp):
    def __init__(self, op, args):
        self.op = op
        self.args = args

    def __str__(self):
        s = '(' + str(self.op)
        for elt in self.args:
            s += ' ' + str(elt)
        s += ')'
        return s

    def __repr__(self):
        s = 'ApExp(' + repr(self.op) + ', ['
        s += ', '.join([ repr(elt) for elt in self.args ])
        s += '])'
        return s

# an Sxp can be a NilSxp, a NumSxp, a SymSxp, or a ListSxp
class Sxp: pass

class NilSxp(Sxp):
    def __str__(self):
        return '()'

    def __repr__(self):
        return 'NilSxp()'

class NumSxp(Sxp):
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return str(self.number)

    def __repr__(self):
        return 'NumSxp(' + repr(self.number) + ')'

class SymSxp(Sxp):
    def __init__(self, symval):
        self.symval = symval

    def __str__(self):
        return str(self.symval)

    def __repr__(self):
        return 'SymSxp(' + repr(self.symval) + ')'

class ListSxp(Sxp):
    def __init__(self, carval, cdrval):
        self.carval = carval
        self.cdrval = cdrval

    def __str__(self):
        s = '('
        car, cdr = self.carval, self.cdrval
        i = 0
        while True:
            if i > 0:
                s += ' '
            s += str(car)
            if isinstance(cdr, ListSxp):
                car, cdr = cdr.carval, cdr.cdrval
            elif isinstance(cdr, NilSxp):
                break
            else:
                s += '. ' + str(cdr)
                break
            i += 1
        s += ')'
        return s

    def __repr__(self):
        s = 'ListSxp(' + repr(self.carval)
        s += ', ' + repr(self.cdrval) + ')'
        return s

class Closure(Sxp):
    def __init__(self, f, environment):
        self.f = f
        self.environment = environment

    def __str__(self):
        return '<closure>'

    def __repr__(self):
        s = 'Closure(' + repr(self.f)
        s += ', ' + repr(self.environment) + ')'
        return s

class PrimOp(Sxp):
    def __init__(self, name, f, nargs):
        # the name of this primitive operation, e.g. "+"
        self.name = name

        # a function that implements this primitive operation
        # it should accept a single parameters, which is a list of
        # evaluated arguments
        self.f = f

        # the number of arguments this op requires
        self.nargs = nargs

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<primop ' + self.name + '>'
