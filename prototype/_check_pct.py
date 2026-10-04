# -*- coding: utf-8 -*-
"""Audita literales usados con el operador % que tienen % sueltos (p. ej. width:100%)."""
import ast
import io
import re
import sys

SPEC = re.compile(
    r"%(?:%|\([A-Za-z_][A-Za-z_0-9]*\)[-+ #0]*\d*(?:\.\d+)?[hlL]?[diouxXeEfFgGcrsa]"
    r"|[-+ #0]*\d*(?:\.\d+)?[hlL]?[diouxXeEfFgGcrsa%])"
)


def main(paths):
    for p in paths:
        src = io.open(p, encoding="utf-8").read()
        tree = ast.parse(src, p)
        for n in ast.walk(tree):
            if not isinstance(n, ast.BinOp) or not isinstance(n.op, ast.Mod):
                continue
            left = n.left
            if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
                continue
            lit = left.value
            limpio = SPEC.sub("", lit)
            if "%" in limpio:
                for m in re.finditer(r"%", limpio):
                    i = m.start()
                    ctx = lit[max(0, i - 26): i + 12].replace("\n", " ")
                    print("%s:%d  ctx=%s" % (p, n.lineno, ascii(ctx)))
                    break


if __name__ == "__main__":
    main(sys.argv[1:])