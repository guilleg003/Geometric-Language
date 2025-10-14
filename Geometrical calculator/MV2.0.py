# ==============================
# VM / Intérprete de Figuras con GUI (Tkinter) y DIBUJO
# ==============================
# Cambios pedidos:
# - 0 => círculo vacío (borde blanco, sin relleno).
# - 1 => círculo naranja RELLENO.
# - 2 => línea naranja (trazo).
# - 3..9 => polígonos naranjas RELLENOS.
# - Resto igual: fondo negro, entrada/salida y representación por dígitos.
#
# Ejemplo para GUI:
# heptagono_blanco_print barra_negra_vertical 5 circulo_negro 5 barra_blanca_vertical

import re
import sys
import math
from collections import deque

# ---------- Léxico: nombres de figuras -> símbolos ----------
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

# ---------- Lexer ----------
def lex(code: str):
    """Convierte el programa en lista de tokens: números, ('ID', nombre), o símbolos."""
    raw = code.replace("\n", " ").split()
    out = []
    for t in raw:
        if t in {"(", ")", ";"}:
            out.append(t); continue
        if t in TOKENS:
            out.append(TOKENS[t]); continue
        if t in SYMS:
            out.append(t); continue
        try:
            n = float(t) if "." in t else int(t)
            out.append(n); continue
        except ValueError:
            pass
        if re.fullmatch(r"[A-Za-z_]\w*", t):
            out.append(("ID", t)); continue
        raise SyntaxError(f"Token no reconocido: {t}")
    return out

# ---------- Operadores y precedencias ----------
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
    """Shunting-yard: infijo -> RPN."""
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

# ---------- Evaluación de expresiones ----------
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

# ---------- Parser de sentencias / bloques ----------
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

# ---------- Intérprete ----------
class Interpreter:
    def __init__(self, output_cb=None):
        self.env = {}
        self.exprvm = VMExpr(self.env)
        self.output_cb = output_cb if output_cb is not None else print
        self.last_printed_value = None  # guardamos el último valor impreso

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
            self.last_printed_value = val
            self.output_cb(val)
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

# ---------- GUI (Tkinter) con fondo negro y dibujo ----------
def launch_gui():
    import tkinter as tk

    ORANGE = "#FFA500"  # color naranja

    # --- Ventana base (negro) ---
    root = tk.Tk()
    root.title("VM Figuras")
    root.configure(bg="black")
    root.geometry("980x640")
    root.minsize(900, 560)

    # Utilidades de estilo rápido
    def mk_label(parent, text, size=11, bold=False):
        font = ("Segoe UI", size, "bold" if bold else "normal")
        return tk.Label(parent, text=text, fg="white", bg="black", font=font)

    def mk_button(parent, text, cmd=None):
        return tk.Button(parent, text=text, command=cmd, fg="white", bg="#222222",
                         activebackground="#333333", activeforeground="white",
                         relief="flat", padx=10, pady=6)

    # --- Layout superior: Entrada y Botones ---
    top = tk.Frame(root, bg="black")
    top.pack(fill="x", padx=12, pady=10)

    mk_label(top, "QUE OPERACION DESEAS REALIZAR?", size=12, bold=True).pack(anchor="w", pady=(0,6))

    input_box = tk.Text(top, height=4, wrap="word",
                        fg="white", bg="#111111", insertbackground="white",
                        relief="flat", padx=8, pady=8)
    input_box.pack(fill="x", expand=False)
    input_box.insert("1.0", "heptagono_blanco_print barra_negra_vertical 5 circulo_negro 5 barra_blanca_vertical")

    btn_row = tk.Frame(top, bg="black")
    btn_row.pack(fill="x", pady=8)
    btn_ejecutar = mk_button(btn_row, "Ejecutar")
    btn_reiniciar = mk_button(btn_row, "Reiniciar VM")
    btn_limpiar = mk_button(btn_row, "Limpiar salida")
    btn_ejecutar.pack(side="left")
    btn_reiniciar.pack(side="left", padx=8)
    btn_limpiar.pack(side="left")

    # --- Zona central: Salida (texto) y Polígono (canvas) ---
    middle = tk.Frame(root, bg="black")
    middle.pack(fill="both", expand=True, padx=12, pady=(0,12))

    # Columna izquierda: salida
    left = tk.Frame(middle, bg="black")
    left.pack(side="left", fill="both", expand=True, padx=(0,6))

    mk_label(left, "Salida:", size=12, bold=True).pack(anchor="w")
    output_box = tk.Text(left, height=10, wrap="word",
                         fg="white", bg="#111111", insertbackground="white",
                         relief="flat", padx=8, pady=8)
    output_box.pack(fill="both", expand=True)

    # Columna derecha: polígono
    right = tk.Frame(middle, bg="black")
    right.pack(side="left", fill="both", expand=True, padx=(6,0))

    mk_label(right, "Polígono:", size=12, bold=True).pack(anchor="w")
    canvas = tk.Canvas(right, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # ---- Salida helper
    def append_output(msg):
        output_box.insert("end", str(msg) + "\n")
        output_box.see("end")

    # ---- VM con callback de salida
    vm = Interpreter(output_cb=append_output)

    # ==========================
    # DIBUJO DE POLÍGONOS
    # ==========================

    def clear_canvas():
        canvas.delete("all")

    def draw_circle(cx, cy, r, fill_color=None, outline_color=None, outline_width=2):
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=fill_color if fill_color else "",
                           outline=outline_color if outline_color else "",
                           width=outline_width)

    def draw_line(cx, cy, length, color, width=4):
        canvas.create_line(cx - length/2, cy, cx + length/2, cy,
                           fill=color, width=width, capstyle="round")

    def regular_polygon_points(cx, cy, r, n, rotation_deg=-90):
        pts = []
        rot = math.radians(rotation_deg)
        for k in range(n):
            ang = rot + 2 * math.pi * k / n
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            pts.extend([x, y])
        return pts

    def draw_ngon(cx, cy, r, n, fill_color, outline_color=None, outline_width=2):
        pts = regular_polygon_points(cx, cy, r, n)
        canvas.create_polygon(pts,
                              fill=fill_color,
                              outline=outline_color if outline_color else fill_color,
                              width=outline_width)

    def draw_digit_shape(d, cx, cy, size):
        """
        Dibuja la 'figura-dígito' centrada en (cx,cy).
        Reglas:
          - 0 => círculo VACÍO (borde blanco, sin relleno).
          - 1 => círculo naranja RELLENO.
          - 2 => línea naranja.
          - 3..9 => n-gono naranja RELLENO.
        """
        r = size * 0.35
        if d == 0:
            # círculo vacío: borde blanco
            draw_circle(cx, cy, r, fill_color=None, outline_color="white", outline_width=2)
        elif d == 1:
            # círculo naranja relleno
            draw_circle(cx, cy, r, fill_color=ORANGE, outline_color=ORANGE, outline_width=2)
        elif d == 2:
            # línea naranja
            draw_line(cx, cy, length=size * 0.7, color=ORANGE, width=5)
        elif 3 <= d <= 9:
            # n-gono naranja relleno
            draw_ngon(cx, cy, r, d, fill_color=ORANGE, outline_color=ORANGE, outline_width=2)
        else:
            # fuera de rango (no debería ocurrir al ir dígito a dígito)
            pass

    def draw_value(val):
        """Dibuja según la regla. Val debe ser numérico."""
        clear_canvas()
        if isinstance(val, bool):
            append_output("[Aviso] Resultado booleano: no se dibuja polígono.")
            return

        if isinstance(val, float):
            if abs(val - round(val)) < 1e-9:
                val = int(round(val))

        if not isinstance(val, int):
            append_output("[Aviso] Resultado no entero: no se dibuja polígono.")
            return

        # Para negativos: avisamos y usamos valor absoluto para dibujar
        if val < 0:
            append_output("[Aviso] Valor negativo: se dibuja usando valor absoluto.")
            val = abs(val)

        digits = [int(ch) for ch in str(val)] if val != 0 else [0]

        # Layout
        w = canvas.winfo_width() or 400
        h = canvas.winfo_height() or 300
        n = len(digits)
        cell_w = min(160, max(80, (w - 40) // max(1, n)))
        size = cell_w
        total_w = n * cell_w
        start_x = (w - total_w) / 2 + cell_w / 2
        cy = h / 2

        for idx, d in enumerate(digits):
            cx = start_x + idx * cell_w
            draw_digit_shape(d, cx, cy, size)

    # ---- Handlers de botones
    def on_ejecutar():
        code = input_box.get("1.0", "end").strip()
        if not code:
            return
        try:
            vm.last_printed_value = None
            vm.run(code)
            val = vm.last_printed_value
            if val is not None:
                draw_value(val)
            else:
                append_output("[Info] No se ha llamado a PRINT: no hay resultado para dibujar.")
                clear_canvas()
        except Exception as e:
            append_output(f"Error: {e}")
            clear_canvas()

    def on_reiniciar():
        vm.env.clear()
        vm.exprvm = VMExpr(vm.env)
        vm.last_printed_value = None
        append_output("[VM reiniciada: variables borradas]")
        clear_canvas()

    def on_limpiar():
        output_box.delete("1.0", "end")
        clear_canvas()

    btn_ejecutar.configure(command=on_ejecutar)
    btn_reiniciar.configure(command=on_reiniciar)
    btn_limpiar.configure(command=on_limpiar)

    # Redibujar al cambiar de tamaño
    def on_resize(event):
        if vm.last_printed_value is not None:
            draw_value(vm.last_printed_value)

    canvas.bind("<Configure>", on_resize)

    root.mainloop()

# ---------- Main ----------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            Interpreter().run(f.read())
    else:
        launch_gui()
