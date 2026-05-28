import tkinter as tk
from tkinter import scrolledtext, ttk

class CompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Two-Pass Compiler")
        self.root.geometry("900x600")

        # Sol Panel: Kaynak Kod Giriş Alanı
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(left_frame, text="Source Code:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.source_text = scrolledtext.ScrolledText(left_frame, width=40, height=30)
        self.source_text.pack(fill=tk.BOTH, expand=True)

        self.compile_btn = tk.Button(left_frame, text="Compile Code", bg="lightblue", command=self.compile_code)
        self.compile_btn.pack(pady=10, fill=tk.X)

        # Sağ Panel: Çıktı Sekmeleri
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Sekme Alanlarını Oluşturma
        self.tokens_tab = scrolledtext.ScrolledText(self.notebook, state=tk.DISABLED)
        self.symbol_table_tab = scrolledtext.ScrolledText(self.notebook, state=tk.DISABLED)
        self.errors_tab = scrolledtext.ScrolledText(self.notebook, state=tk.DISABLED)

        self.notebook.add(self.tokens_tab, text="Lexer Output (Pass 1)")
        self.notebook.add(self.symbol_table_tab, text="Symbol Table")
        self.notebook.add(self.errors_tab, text="Errors")

    def compile_code(self):
        from lexer import Lexer
        from parser import Parser # Parser'ı projeye dahil ediyoruz

        source_code = self.source_text.get("1.0", tk.END).strip()
        if not source_code:
            return

        # --- PASS 1: Lexical Analysis ---
        lexer = Lexer(source_code)
        tokens, symbol_table, lexer_errors = lexer.tokenize()

        token_output = f"{'Line':<10}{'Token':<20}{'Type'}\n" + "-"*45 + "\n"
        for t in tokens:
            if t.type.name != "EOF":
                token_output += f"{t.line:<10}{t.value:<20}{t.type.name}\n"
        self.write_to_tab(self.tokens_tab, token_output)

        # --- PASS 2: Syntax and Semantic Analysis ---
        parser = Parser(tokens, symbol_table)
        ast = parser.parse()
        parser_errors = parser.errors

        # Sembol Tablosunu Güncelle (Artık tipleri de biliyoruz)
        sym_output = f"{'Identifier':<15}{'Type':<10}{'Scope':<10}{'Line'}\n" + "-"*45 + "\n"
        for identifier, attrs in parser.symbol_table.items():
            t_type = attrs.get('type') or 'Unknown'
            sym_output += f"{identifier:<15}{t_type:<10}{attrs['scope']:<10}{attrs['line_declared']}\n"
        self.write_to_tab(self.symbol_table_tab, sym_output)

        # Hataları Birleştir ve Ekrana Yazdır
        all_errors = lexer_errors + parser_errors
        if all_errors:
            err_output = "\n".join(all_errors)
        else:
            err_output = "Compilation Successful!\n0 Lexical Errors\n0 Syntax Errors\n0 Semantic Errors\n\nGenerated AST:\n"
            for node in ast:
                err_output += f"{node}\n"
        
        self.write_to_tab(self.errors_tab, err_output)
        
    def write_to_tab(self, tab, text):
        tab.config(state=tk.NORMAL)
        tab.delete("1.0", tk.END)
        tab.insert(tk.END, text)
        tab.config(state=tk.DISABLED)