import ast 

nilValue = ast.NilSxp()
trueValue = ast.SymSxp('T')

def primoplus(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    assert(isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp))
    return ast.NumSxp(v1.number + v2.number)

def primominus(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    assert(isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp))
    return ast.NumSxp(v1.number - v2.number)

def primomult(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    assert(isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp))
    return ast.NumSxp(v1.number * v2.number)

def primodiv(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    assert(isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp))
    return ast.NumSxp(v1.number // v2.number)

def primolt(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    assert(isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp))
    if v1.number < v2.number:
        return trueValue
    return nilValue

def primogt(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    assert(isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp))
    if v1.number > v2.number:
        return trueValue
    return nilValue

def primoeq(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    if isinstance(v1, ast.NumSxp) and isinstance(v2, ast.NumSxp):
        if v1.number == v2.number:
            return trueValue
    if isinstance(v1, ast.SymSxp) and isinstance(v2, ast.SymSxp):
        if v1.symval == v2.symval:
            return trueValue
    if v1 == nilValue and v2 == nilValue:
        return trueValue
    else:
        return nilValue

def primocons(args):
    assert(len(args) == 2)
    v1 = args[0]
    v2 = args[1]
    if not isinstance(v2, ast.ListSxp) and v2 != nilValue:
        raise RuntimeError("Second argument in cons not list or nil sxp")
    else:
        return ast.ListSxp(v1, v2)

def primocar(args):
    assert(len(args) == 1)
    listobj = args[0]
    assert(isinstance(listobj, ast.ListSxp))
    return listobj.carval

def primocdr(args):
    assert(len(args) == 1)
    listobj = args[0]
    assert(isinstance(listobj, ast.ListSxp))
    return listobj.cdrval

def primonum(args):
    assert(len(args) == 1)
    if isinstance(args[0], ast.NumSxp):
        return trueValue
    return nilValue

def primosym(args):
    assert(len(args) == 1)
    if isinstance(args[0], ast.SymSxp):
        return trueValue
    return nilValue

def primolist(args):
    assert(len(args) == 1)
    if isinstance(args[0], ast.ListSxp):
        return trueValue
    return nilValue

def primonull(args):
    assert(len(args) == 1)
    if isinstance(args[0], ast.NilSxp):
        return trueValue
    return nilValue

def primoprimop(args):
    assert(len(args) == 1)
    if isinstance(args[0], ast.PrimOp):
        return trueValue
    return nilValue

def primoclose(args):
    assert(len(args) == 1)
    if isinstance(args[0], ast.Closure):
        return trueValue
    return nilValue

def primoprint(args):
    if len(args) == 1:
        print(str(args[0]))
        return args[0]
    return nilValue

fxns = {
    '+': ast.PrimOp('+', primoplus, 2), 
    '-': ast.PrimOp('-', primominus, 2), 
    '*': ast.PrimOp('*', primomult, 2), 
    '/': ast.PrimOp('/', primodiv, 2), 
    '<': ast.PrimOp('<', primolt, 2), 
    '>': ast.PrimOp('>', primogt, 2), 
    '=': ast.PrimOp('=', primoeq, 2), 
    'cons': ast.PrimOp('cons', primocons, 2), 
    'car': ast.PrimOp('car', primocar, 1), 
    'cdr': ast.PrimOp('cdr', primocdr, 1), 
    'number?': ast.PrimOp('number?', primonum, 1), 
    'symbol?': ast.PrimOp('symbol?', primosym, 1), 
    'list?': ast.PrimOp('list?', primolist, 1), 
    'null?': ast.PrimOp('null?', primonull, 1), 
    'print': ast.PrimOp('print', primoprint, 1), 
    'primop?': ast.PrimOp('primop?', primoprimop, 1), 
    'closure?': ast.PrimOp('closure?', primoclose, 1)
}

globalEnv = ast.Environment(fxns, None)

def eval(exp, rho):
    assert(isinstance(exp,ast.Exp))
    sexp = realEval(exp, rho)
    assert(isinstance(sexp,ast.Sxp))
    return sexp

def realEval(exp,rho):
    if isinstance(exp, ast.ValExp):
        return exp.sxp

    elif isinstance(exp, ast.Lambda):
        return ast.Closure(exp, rho)

    elif isinstance(exp, ast.VarExp):
        currEnv = rho
        while True:
            if exp.name in currEnv.values:
                return currEnv.values[exp.name]
            elif currEnv.enclosed == None:
                currEnv.values[exp.name] = nilValue
                return nilValue
            else:
                currEnv = currEnv.enclosed

    ###############

    elif isinstance(exp, ast.ApExp):
        if exp.op == 'if':
            if isinstance(eval(exp.args[0], rho), ast.NilSxp):
                return eval(exp.args[2], rho)
            else:
                return eval(exp.args[1], rho)

        elif exp.op == 'while':
            while not (isinstance(eval(exp.args[0], rho), ast.NilSxp)):
                eval(exp.args[1], rho)
            return nilValue

        elif exp.op == 'set':
            currEnv = rho
            val = eval(exp.args[1], rho)
            while True:
                if exp.args[0] in currEnv.values:
                    currEnv.values[exp.args[0]] = val
                    return val
                elif currEnv.enclosed == None:
                    currEnv.values[exp.args[0]] = val
                    return val
                else:
                    currEnv = currEnv.enclosed

        elif exp.op == 'begin':
            for i in range(len(exp.args)):
                if i == len(exp.args) - 1:
                    return eval(exp.args[i], rho)
                eval(exp.args[i], rho)

        else:
            x = eval(exp.op, rho)
            if isinstance(x, ast.PrimOp):
                if len(exp.args) == x.nargs:
                    arglst = []
                    for i in range(len(exp.args)):
                        arglst.append(eval(exp.args[i], rho))
                    methodToCall = getattr(x, 'f')
                    result = methodToCall(arglst)
                    return result

            elif isinstance(x, ast.Closure):
                assert(isinstance(x.f, ast.Lambda))
                if len(x.f.formals) == len(exp.args):
                    vals = {}
                    for i in range(len(exp.args)):
                        vals[x.f.formals[i]] = eval(exp.args[i], rho)
                    newEnv = ast.Environment(vals, x.environment)
                    result = eval(x.f.body, newEnv)
                    return result
                raise RuntimeError("Num args don't match in closure")

    else:
        raise RuntimeError("End All")