import ast
import eval

class TokenizingReader:
    def __init__(self, cin, cout):
        self.cin = cin
        self.cout = cout
        self.line = ''
        self.lineNumber = 0
        self.continuePrompt(False)

    def continuePrompt(self, b):
        if b:
            self.prompt = '  > '
        else:
            self.prompt = '--> '

    def get(self):
        # read a line if our buffer is empty
        if self.line == '':
            if self.cout is not None:
                self.cout.write(self.prompt)
                self.cout.flush()
            self.line = self.cin.readline()
            if self.line != '' and self.line[-1] != '\n':
                self.line = self.line + '\n'
            self.lineLen = len(self.line)
            self.lineNumber += 1

        # end of file?
        if self.line == '':
            return (None, self.lineNumber, 0)

        # skip whitespace (except newlines)
        while self.line[0] != '\n' and self.line[0].isspace():
            self.line = self.line[1:]

        # skip comments
        if self.line[0] == ';':
            self.line = self.line[-1:]

        # end of line, parentheses, or quote?
        if self.line[0] in "()\n'":
            v = (self.line[0], self.lineNumber, self.lineLen-len(self.line)+1)
            self.line = self.line[1:]
            return v

        # scan a name
        i = 1
        while i < len(self.line) and not self.line[i].isspace() and self.line[i] not in '();':
            i += 1
        v = (self.line[:i], self.lineNumber, self.lineLen-len(self.line)+1)
        self.line = self.line[i:]
        return v

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def input(self, i):
        if i < 0: return (None, -1)

        # expression
        (expression, j) = self.expression(i)
        if j >= 0:
            return (expression, j)

        return (None, -1)

    def expression(self, i):
        if i < 0: return (None, -1)

        # value
        value, j = self.value(i)
        if j >= 0:
            return (value, j)

        # variable
        variable, j = self.variable(i)
        if j >= 0:
            v = ast.VarExp(variable)
            return (v, j)

        # ( if expression expression expression )
        j = self.mustBe('(', i)
        j = self.mustBe('if', j)
        (e1, j) = self.expression(j)
        (e2, j) = self.expression(j)
        (e3, j) = self.expression(j)
        j = self.mustBe(')', j)
        if j >= 0:
            elt = ast.ApExp('if', [e1, e2, e3])
            return (elt, j)

        # ( while expression expression )
        j = self.mustBe('(', i)
        j = self.mustBe('while', j)
        (e1, j) = self.expression(j)
        (e2, j) = self.expression(j)
        j = self.mustBe(')', j)
        if j >= 0:
            elt = ast.ApExp('while', [e1, e2])
            return (elt, j)

        # ( set variable expression )
        j = self.mustBe('(', i)
        j = self.mustBe('set', j)
        (variable, j) = self.variable(j)
        (e1, j) = self.expression(j)
        j = self.mustBe(')', j)
        if j >= 0:
            elt = ast.ApExp('set', [variable, e1])
            return (elt, j)

        # ( begin expression+ )
        j = self.mustBe('(', i)
        j = self.mustBe('begin', j)
        elist = []
        (e1, j) = self.expression(j)
        k = j
        while j >= 0:
            k = j
            elist.append(e1)
            (e1, j) = self.expression(j)
        j = k
        j = self.mustBe(')', j)
        if j >= 0:
            elt = ast.ApExp('begin', elist)
            return (elt, j)

        # ( expression+ )
        j = self.mustBe('(', i)
        elist = []
        (e1, j) = self.expression(j)
        k = j
        while j >= 0:
            k = j
            elist.append(e1)
            (e1, j) = self.expression(j)
        j = k
        j = self.mustBe(')', j)
        if j >= 0:
            elt = ast.ApExp(elist[0], elist[1:])
            return (elt, j)

        return (None, -1)

    def value(self, i):
        if i < 0: return (None, -1)

        # integer
        (sxp, j) = self.integer(i)
        if j >= 0:
            return (ast.ValExp(sxp), j)

        # quoted-const
        (sxp, j) = self.quotedConst(i)
        if j >= 0:
            return (ast.ValExp(sxp), j)

        # ( lambda arglist expression )
        j = self.mustBe('(', i)
        j = self.mustBe('lambda', j)
        argList, j = self.argList(j)
        expression, j = self.expression(j)
        j = self.mustBe(')', j)
        if j >= 0:
            f = ast.Lambda(argList, expression)
            return (f, j)

        return (None, -1)

    def argList(self, i):
        if i < 0: return (None, -1)

        # ( variable* )
        i = self.mustBe('(', i)
        vlist = []
        j = i
        (variable, i) = self.variable(i)
        while i >= 0:
            j = i
            vlist.append(variable)
            (variable, i) = self.variable(i)
        i = j
        i = self.mustBe(')', i)
        if i >= 0:
            return (vlist, i)

        return (None, -1)

    def quotedConst(self, i):
        if i < 0: return (None, -1)

        # 'S-expression
        i = self.mustBe("'", i)
        (sxp, i) = self.sExpression(i)
        if i >= 0:
            return (sxp, i)

        return (None, -1)

    def sExpression(self, i):
        if i < 0: return (None, -1)

        # integer
        (sxp, j) = self.integer(i)
        if j >= 0:
            return (sxp, j)

        # symbol
        (name, j) = self.symbol(i)
        if j >= 0:
            return (ast.SymSxp(name), j)

        # ( S-expression* )
        j = self.mustBe('(', i)
        slist = []
        k = j
        (s1, j) = self.sExpression(j)
        while j >= 0:
            k = j
            slist.append(s1)
            (s1, j) = self.sExpression(j)
        j = k
        j = self.mustBe(')', j)
        if j >= 0:
            # form a linked list
            tail = eval.nilValue
            for elt in slist[::-1]:
                tail = ast.ListSxp(elt, tail)
            return (tail, j)

        return (None, -1)

    def symbol(self, i):
        if i < 0: return (None, -1)

        # name
        (name, j) = self.name(i)
        if j >= 0:
            return (name, j)

        return (None, -1)

    def variable(self, i):
        if i < 0: return (None, -1)

        # name
        (name, j) = self.name(i)
        if j >= 0:
            return (name, j)

        return (None, -1)

    def integer(self, i):
        if i < 0: return (None, -1)

        # sequence of digits, possibly preceded by minus sign
        (v, j) = self.raw(i)
        if j >= 0:
            if  (len(v) > 0 and v.isdigit()) or \
                (len(v) > 1 and v[0] == '-' and v[1:].isdigit()):
                n = int(v)
                return (ast.NumSxp(n), j)

        return (None, -1)

    def name(self, i):
        if i < 0: return (None, -1)

        # any sequence of characters not an integer, and not containing
        # a blank or any of the following characters: ( ) ;

        (v, j) = self.raw(i)
        if j < 0 or '(' in v or ')' in v or ';' in v or ' ' in v:
            return (None, -1)
        if v.isdigit() or len(v) > 1 and v[0] == '-' and v[1:].isdigit():
            return (None, -1)

        return (v, j)

    def mustBe(self, name, i):
        if i < 0: return -1

        (v, j) = self.raw(i)
        if j >= 0 and v == name:
            return j

        return -1

    def raw(self, i):
        if i < 0: return (None, -1)
        if i >= len(self.tokens): return (None, -1)
        return (self.tokens[i][0], i+1)

    def finished(self, i):
        return i == len(self.tokens)
