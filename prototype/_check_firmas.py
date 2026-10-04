# -*- coding: utf-8 -*-
"""Audita llamadas a funciones de lib_ui/lib_charts contra sus firmas reales."""
import ast
import inspect
from inspect import Parameter as P
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_charts
import lib_ui

FUNCIONES = {}
for mod in (lib_ui, lib_charts):
    for nom, obj in vars(mod).items():
        if inspect.isfunction(obj) and not nom.startswith("_"):
            FUNCIONES.setdefault(nom, obj)


def chequear(paths):
    errores = 0
    for p in paths:
        arbol = ast.parse(io.open(p, encoding="utf-8").read(), p)
        for n in ast.walk(arbol):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            nom = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
            if nom not in FUNCIONES:
                continue
            fn = FUNCIONES[nom]
            sig = inspect.signature(fn)
            params = [q for q in sig.parameters if q != "self"]
            varargs = any(sig.parameters[q].kind in (P.VAR_POSITIONAL, P.VAR_KEYWORD)
                          for q in sig.parameters)
            pos = [q for q in sig.parameters.values()
                   if q.kind in (P.POSITIONAL_ONLY, P.POSITIONAL_OR_KEYWORD)]
            npos = len(n.args)
            kw = [k.arg for k in n.keywords if k.arg]
            for k in kw:
                if k not in sig.parameters:
                    print("%s:%d  %s() kwarg desconocido %r  (acepta: %s)"
                          % (p, n.lineno, nom, k, ", ".join(params)))
                    errores += 1
            if not varargs and npos > len(pos):
                print("%s:%d  %s() %d posicionales, max %d" % (p, n.lineno, nom, npos, len(pos)))
                errores += 1
            elif not varargs:
                sin_def = len(pos) - len([q for q in pos
                                          if q.default is not inspect.Parameter.empty])
                if npos + len(kw) < sin_def:
                    print("%s:%d  %s() faltan %d arg(s) obligatorios"
                          % (p, n.lineno, nom, sin_def - (npos + len(kw))))
                    errores += 1
    print("\n%d problema(s) de firma." % errores)
    return errores


if __name__ == "__main__":
    sys.exit(1 if chequear(sys.argv[1:]) else 0)