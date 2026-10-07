"""Kalkulator desktop bergaya modern, dibuat hanya dengan Tkinter bawaan."""

import ast
import operator
import tkinter as tk


class ModernCalculator(tk.Tk):
    """Jendela utama kalkulator beserta logika dan interaksinya."""

    # Warna dark mode
    BG = "#17181C"
    PANEL = "#202126"
    DISPLAY = "#17181C"
    TEXT = "#F4F5F7"
    MUTED = "#A9ABB4"
    NUMBER = "#2A2C33"
    OPERATOR = "#3A3C45"
    ACCENT = "#4DA3FF"
    DANGER = "#D65D5D"

    def __init__(self):
        super().__init__()
        self.title("Kalkulator")
        self.geometry("390x620")
        self.minsize(330, 520)
        self.configure(bg=self.BG)

        self.expression = ""
        self.display_value = tk.StringVar(value="0")
        self._build_ui()
        self._bind_keyboard()

    def _build_ui(self):
        """Menyusun layar dan kisi tombol."""
        container = tk.Frame(self, bg=self.BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="KALKULATOR",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 10, "bold"),
            anchor="e",
        ).pack(fill="x", pady=(4, 0))

        # Label lebih bersih daripada Entry: tanpa frame dan selalu rata kanan.
        tk.Label(
            container,
            textvariable=self.display_value,
            bg=self.DISPLAY,
            fg=self.TEXT,
            font=("Segoe UI", 32, "normal"),
            anchor="e",
            justify="right",
            padx=4,
            pady=18,
        ).pack(fill="x", pady=(0, 14))

        keypad = tk.Frame(container, bg=self.BG)
        keypad.pack(fill="both", expand=True)
        for index in range(5):
            keypad.rowconfigure(index, weight=1, uniform="row")
        for index in range(4):
            keypad.columnconfigure(index, weight=1, uniform="column")

        buttons = [
            ("C", 0, 0, "clear"), ("⌫", 0, 1, "backspace"), ("%", 0, 2, "operator"), ("÷", 0, 3, "operator"),
            ("7", 1, 0, "number"), ("8", 1, 1, "number"), ("9", 1, 2, "number"), ("×", 1, 3, "operator"),
            ("4", 2, 0, "number"), ("5", 2, 1, "number"), ("6", 2, 2, "number"), ("−", 2, 3, "operator"),
            ("1", 3, 0, "number"), ("2", 3, 1, "number"), ("3", 3, 2, "number"), ("+", 3, 3, "operator"),
            ("±", 4, 0, "operator"), ("0", 4, 1, "number"), (".", 4, 2, "number"), ("=", 4, 3, "equals"),
        ]
        for label, row, column, kind in buttons:
            self._make_button(keypad, label, row, column, kind)

    def _make_button(self, parent, label, row, column, kind):
        """Membuat tombol flat dan memasang efek hover."""
        palette = {
            "number": (self.NUMBER, "#383B45", self.TEXT),
            "operator": (self.OPERATOR, "#4A4D58", self.TEXT),
            "equals": (self.ACCENT, "#76BAFF", "#FFFFFF"),
            "clear": ("#442C31", "#5B3940", "#FFB5B5"),
            "backspace": (self.OPERATOR, "#4A4D58", self.TEXT),
        }
        base, hover, foreground = palette[kind]
        button = tk.Label(
            parent, text=label, bg=base, fg=foreground,
            font=("Segoe UI", 18, "bold" if kind == "equals" else "normal"),
            cursor="hand2", anchor="center", bd=0, relief="flat",
        )
        button.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        button.bind("<Enter>", lambda _event: button.configure(bg=hover))
        button.bind("<Leave>", lambda _event: button.configure(bg=base))
        button.bind("<Button-1>", lambda _event: self._press(label))
        

    def _bind_keyboard(self):
        """Mendukung input keyboard umum."""
        self.bind("<Key>", self._on_key)
        self.bind("<Return>", lambda _event: self._calculate())
        self.bind("<KP_Enter>", lambda _event: self._calculate())
        self.bind("<BackSpace>", lambda _event: self._backspace())
        self.bind("<Escape>", lambda _event: self._clear())

    def _on_key(self, event):
        key = event.char
        if key in "0123456789.+-*/%":
            self._press({"*": "×", "/": "÷", "-": "−"}.get(key, key))

    def _press(self, value):
        """Mengarahkan klik tombol ke aksi yang sesuai."""
        if value == "C":
            self._clear()
        elif value == "⌫":
            self._backspace()
        elif value == "=":
            self._calculate()
        elif value == "±":
            self._toggle_sign()
        else:
            self.expression += value
            self._show(self.expression)

    def _clear(self):
        self.expression = ""
        self._show("0")

    def _backspace(self):
        self.expression = self.expression[:-1]
        self._show(self.expression or "0")

    def _toggle_sign(self):
        """Mengubah tanda angka terakhir tanpa mengevaluasi seluruh ekspresi."""
        if not self.expression:
            self.expression = "-"
        elif self.expression[-1].isdigit() or self.expression[-1] == ".":
            # Membungkus operand terakhir; aman untuk ekspresi seperti 4+(-2).
            import re
            match = re.search(r"(?<![\d.])(-?\d*\.?\d+)$", self.expression)
            if match:
                number = match.group(1)
                replacement = number[1:] if number.startswith("-") else "-" + number
                self.expression = self.expression[:match.start()] + replacement
        self._show(self.expression or "0")

    def _calculate(self):
        if not self.expression:
            return
        try:
            result = self._safe_evaluate(self.expression)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(result)
            self._show(self.expression)
        except (ArithmeticError, SyntaxError, ValueError, TypeError):
            self.expression = ""
            self._show("Error")

    def _safe_evaluate(self, expression):
        """Evaluasi matematika sederhana tanpa eval(), sehingga input tetap aman."""
        normalized = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
        allowed = {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.Mod: operator.mod,
            ast.USub: operator.neg, ast.UAdd: operator.pos,
        }

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                return allowed[type(node.op)](visit(node.left), visit(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
                return allowed[type(node.op)](visit(node.operand))
            raise ValueError("Ekspresi tidak didukung")

        return visit(ast.parse(normalized, mode="eval"))

    def _show(self, value):
        """Memotong tampilan yang terlalu panjang agar UI tetap rapi."""
        self.display_value.set(value[-18:] if len(value) > 18 else value)


if __name__ == "__main__":
    ModernCalculator().mainloop()