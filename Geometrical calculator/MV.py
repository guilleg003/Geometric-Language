# ==============================
# VM / Intérprete de Figuras
# ==============================
# Soporta:
# - Aritmética (figuras negras): + - * / % ** // != =  y paréntesis
# - Comparadores y control (figuras blancas): > <  IF ELSE WHILE FOR PRINT
# - Paréntesis pedidos: barra_negra_vertical = (   barra_blanca_vertical = )
# - Sentencias separadas por ;
#
# Ejemplo de entrada:
# heptagono_blanco_print barra_negra_vertical 5 circulo_negro 5 barra_blanca_vertical

import re
import sys
from collections import deque

# ---------- Léxico: nombres de figuras -> símbolos (lo que entiende el interprete))  ----------
TOKENS = {
    # Negras (columna izquierda)
    "circulo_negro": "+",
    "raya_negra": "-",
    "triangulo_negro": "*",
    "cuadrado_negro": "/",
    "pentagono_negro": "%",
    "hexagono_negro": "**",
    "octagono_negro": "//",
    "heptagono_negro": "!=",       # comparación distinta
    "eneagono_negro": "=",         # asignación
    "barra_negra_vertical": "(",   # paréntesis abierto
    "barra_blanca_vertical": ")",  # paréntesis cerrado

    # Blancas (columna derecha)
    "circulo_blanco": ">",         # mayor que
    "raya_blanca": "<",            # menor que
    "triangulo_blanco_if": "IF",
    "cuadrado_blanco_else": "ELSE",
    "pentagono_blanco_while": "WHILE",
    "hexagono_blanco_for": "FOR",
    "heptagono_blanco_print": "PRINT",
}

SYMS = set(TOKENS.keys()) | set(TOKENS.values()) | {";", "(", ")"}

# ---------- Lexer ---------- genera una lista clara de numeros identificadores y simbolos
def lex(code: str):
    """Convierte el programa en lista de tokens: números, ('ID', nombre), o símbolos."""
    raw = code.replace("\n", " ").split()
    out = []
    for t in raw:
        # permitir símbolos literales
        if t in {"(", ")", ";"}:
            out.append(t)
            continue
        # nombres de figura -> símbolo
        if t in TOKENS:
            out.append(TOKENS[t])
            continue
        # símbolo ya reconocido
        if t in SYMS:
            out.append(t)
            continue
        # número
        try:
            n = float(t) if "." in t else int(t)
            out.append(n)
            continue
        except ValueError:
            pass
        # identificador
        if re.fullmatch(r"[A-Za-z_]\w*", t):
            out.append(("ID", t))
            continue
        raise SyntaxError(f"Token no reconocido: {t}")
    return out

# ---------- Operadores y precedencias (para expresiones) ---------- precedencia asociatividad ariedad funcion
OPERADORES = {
    "+":  (2, "left", 2, lambda a, b: a + b),
    "-":  (2, "left", 2, lambda a, b: a - b),
    "*":  (3, "left", 2, lambda a, b: a * b),
    "/":  (3, "left", 2, lambda a, b: a / b),
    "%":  (3, "left", 2, lambda a, b: a % b),
    "//": (3, "left", 2, lambda a, b: a // b),
    "**": (4, "right", 2, lambda a, b: a ** b),
    ">":  (1, "left", 2, lambda a, b: a > b),
    "<":  (1, "left", 2, lambda a, b: a < b),
    "!=": (1, "left", 2, lambda a, b: a != b),
}

def to_rpn(tokens):
    """Shunting-yard: infijo -> RPN    reorganiza los tokens de una expresion usando una pila de operadores. 
    IDs directos a la salida y Operadores se comparan arriba de la fila. Al final se vacia la pila """
    out, stack = [], []
    for t in tokens:
        if isinstance(t, (int, float)) or (isinstance(t, tuple) and t[0] == "ID"):
            out.append(t)
        elif t in OPERADORES:
            p1, assoc1 = OPERADORES[t][0], OPERADORES[t][1]
            while stack and stack[-1] in OPERADORES:
                p2 = OPERADORES[stack[-1]][0]
                if (assoc1 == "left" and p1 <= p2) or (assoc1 == "right" and p1 < p2):
                    out.append(stack.pop()); continue
                break
            stack.append(t)
        elif t == "(":
            stack.append(t)
        elif t == ")":
            while stack and stack[-1] != "(":
                out.append(stack.pop())
            if not stack:
                raise SyntaxError("Paréntesis desbalanceados")
            stack.pop()
        else:
            raise SyntaxError(f"Token inesperado en expresión: {t}")
    while stack:
        op = stack.pop()
        if op in ("(", ")"):
            raise SyntaxError("Paréntesis desbalanceados")
        out.append(op)
    return out

# ---------- Evaluación de expresiones ---------- evalua la rpn con una pila 
class VMExpr:
    def __init__(self, env):
        self.env = env

    def eval_rpn(self, rpn):
        st = deque()
        for t in rpn:
            if isinstance(t, (int, float)):
                st.append(t)
            elif isinstance(t, tuple) and t[0] == "ID":
                name = t[1]
                if name not in self.env:
                    raise NameError(f"Variable no definida: {name}")
                st.append(self.env[name])
            else:
                _, _, _, fn = OPERADORES[t]
                b, a = st.pop(), st.pop()
                st.append(fn(a, b))
        return st[-1] if st else None

    def eval_expr(self, toks):
        return self.eval_rpn(to_rpn(toks))

# ---------- Parser de sentencias / bloques ---------- se utiliza para todas las condiciones, se forman bloques y se les pasa las condiciones
class Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def pop(self):  val = self.peek(); self.i += 1; return val
    def expect(self, wanted):
        got = self.pop()
        if got != wanted:
            raise SyntaxError(f"Se esperaba '{wanted}' y llegó '{got}'")
        return got

    def read_expr_tokens(self, stop_at={";", ")", "ELSE"}):
        depth = 0
        acc = []
        while True:
            cur = self.peek()
            if cur is None:
                break
            if cur == "(":
                depth += 1
            elif cur == ")":
                if depth == 0:
                    break
                depth -= 1
            if depth == 0 and cur in stop_at:
                break
            acc.append(self.pop())
        return acc

    def read_paren_expr(self):
        self.expect("(")
        expr = self.read_expr_tokens(stop_at={")"})
        self.expect(")")
        return expr

    def parse_block(self):
        self.expect("(")
        stmts = []
        while True:
            if self.peek() == ")":
                self.pop()
                break
            stmts.append(self.parse_stmt())
            if self.peek() == ";":
                self.pop()
        return ("BLOCK", stmts)

    def parse_stmt(self):
        cur = self.peek()
        if cur == "PRINT":
            self.pop()
            expr = self.read_paren_expr()
            return ("PRINT", expr)
        if cur == "IF":
            self.pop()
            cond = self.read_paren_expr()
            then_blk = self.parse_block()
            else_blk = None
            if self.peek() == "ELSE":
                self.pop()
                else_blk = self.parse_block()
            return ("IF", cond, then_blk, else_blk)
        if cur == "WHILE":
            self.pop()
            cond = self.read_paren_expr()
            body = self.parse_block()
            return ("WHILE", cond, body)
        if cur == "FOR":
            self.pop()
            self.expect("(")
            init = self.parse_stmt()
            self.expect(";")
            cond = self.read_expr_tokens(stop_at={";"})
            self.expect(";")
            post = self.parse_stmt()
            self.expect(")")
            body = self.parse_block()
            return ("FOR", init, cond, post, body)

        # Asignación: ID = expr
        left = self.pop()
        if not (isinstance(left, tuple) and left[0] == "ID"):
            raise SyntaxError("Se esperaba una sentencia o asignación")
        self.expect("=")
        expr = self.read_expr_tokens(stop_at={";", ")", "ELSE"})
        return ("SET", left[1], expr)

    def parse_program(self):
        prog = []
        while self.peek() is not None:
            prog.append(self.parse_stmt())
            if self.peek() == ";":
                self.pop()
        return ("BLOCK", prog)

# ---------- Intérprete ---------- Coge los bloques del aprser y les aplica la funcion que quede en medio 
class Interpreter:
    def __init__(self):
        self.env = {}
        self.exprvm = VMExpr(self.env)

    def eval_block(self, stmts):
        last = None
        for s in stmts:
            last = self.eval_stmt(s)
        return last

    def eval_stmt(self, node):
        kind = node[0]
        if kind == "BLOCK":
            return self.eval_block(node[1])
        if kind == "PRINT":
            val = self.exprvm.eval_expr(node[1])
            print(val)
            return val
        if kind == "SET":
            name, expr = node[1], node[2]
            val = self.exprvm.eval_expr(expr)
            self.env[name] = val
            return val
        if kind == "IF":
            cond_expr, then_blk, else_blk = node[1], node[2], node[3]
            if self.exprvm.eval_expr(cond_expr):
                return self.eval_stmt(then_blk)
            elif else_blk is not None:
                return self.eval_stmt(else_blk)
            return None
        if kind == "WHILE":
            cond_expr, body = node[1], node[2]
            out = None
            while self.exprvm.eval_expr(cond_expr):
                out = self.eval_stmt(body)
            return out
        if kind == "FOR":
            init, cond, post, body = node[1], node[2], node[3], node[4]
            self.eval_stmt(init)
            out = None
            while self.exprvm.eval_expr(cond):
                out = self.eval_stmt(body)
                self.eval_stmt(post)
            return out
        raise RuntimeError(f"Nodo no soportado: {kind}")

    def run(self, code_str):
        tokens = lex(code_str)
        ast = Parser(tokens).parse_program()
        return self.eval_stmt(ast)

# ---------- Interactivo ----------
def prompt_interactivo():
    vm = Interpreter()
    print("QUE OPERACION DESEAS REALIZAR?")
    while True:
        try:
            linea = input("> ").strip()
        except EOFError:
            break
        if not linea or linea.lower() in {"salir", "exit", "quit"}:
            break
        try:
            vm.run(linea)
        except Exception as e:
            print(f"Error: {e}")

# ---------- Main ----------
if __name__ == "__main__":
    # Si pasas un archivo, lo ejecuta. Si no, abre el prompt.
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            Interpreter().run(f.read())
    else:
        prompt_interactivo()
