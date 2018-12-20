#!/usr/bin/env python3

import sys
import ast, parse, eval

def main():
    print('Scheme interpreter')
    print('October 2017 version')

    if len(sys.argv) == 2:
        repl(sys.argv[1])
    else:
        repl('')

def repl(source):
    fp = None
    if source != '':
        fp = open(source)
        tokenizer = parse.TokenizingReader(fp, sys.stdout)
    else:
        tokenizer = parse.TokenizingReader(sys.stdin, sys.stdout)

    while True:
        tokens = readOne(tokenizer)
        if tokens is None or len(tokens) == 1 and tokens[0][0] == 'quit':
            if fp != None:
                # close the input file, start reading from stdin
                fp.close()
                fp = None
                tokenizer = parse.TokenizingReader(sys.stdin, sys.stdout)
                continue

            # end of file means quitting time
            print()
            break

        parser = parse.Parser(tokens)
        (elt, j) = parser.input(0)
        if j < 0:
            print('Syntax error on input that started on line', tokens[0][1])
            continue
        if not parser.finished(j):
            print('Found extra token beyond end of input:', tokens[j][0])
            continue
        if isinstance(elt, ast.Exp):
            try:
                values = {}
                rho = ast.Environment(values, eval.globalEnv)
                val = eval.eval(elt, rho)
                print(str(val))
            except RuntimeError as err:
                print(err, '(on input that started on line {})'.format(tokens[0][1]))
        else:
            print('Unimplemented (on input that starts on line {})'.format(tokens[0][1]))

def readOne(tokenizer):
    lst = []
    pcount = 0
    tokenizer.continuePrompt(False)
    while True:
        elt = tokenizer.get()
        if elt[0] is None:
            return None
        if elt[0] == '\n':
            if pcount <= 0 and len(lst) > 0:
                return lst
            tokenizer.continuePrompt(len(lst) > 0)
            continue
        if elt[0] == '(':
            pcount += 1
        if elt[0] == ')':
            pcount -= 1
        lst.append(elt)

if __name__ == '__main__':
    main()
