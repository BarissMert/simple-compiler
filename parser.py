from tokens import TokenType
from ast_nodes import *

class Parser:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.pos = -1
        self.current_tok = None
        self.errors = []
        self.declared_vars = {} # Semantik analiz için (Değişken tanımlı mı?)
        self.advance()

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_tok = self.tokens[self.pos]
        return self.current_tok

    def expect(self, expected_type, expected_value=None):
        """Beklenen token gelirse alır, gelmezse hata fırlatır."""
        if self.current_tok.type == expected_type and (expected_value is None or self.current_tok.value == expected_value):
            tok = self.current_tok
            self.advance()
            return tok
        
        expected = expected_value if expected_value else expected_type.name
        self.errors.append(f"Line {self.current_tok.line}: Syntax Error - Expected '{expected}', got '{self.current_tok.value}'")
        self.advance() # Sonsuz döngüyü önlemek için atla
        return None

    def parse(self):
        statements = []
        while self.current_tok.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                self.advance() # Hata durumunda ilerle
        return statements

    def parse_statement(self):
        if self.current_tok.type == TokenType.KEYWORD:
            if self.current_tok.value in ('int', 'float'):
                return self.parse_declaration()
            elif self.current_tok.value == 'if':
                return self.parse_if_statement()
            elif self.current_tok.value == 'while':
                return self.parse_while_statement()
            elif self.current_tok.value == 'print':
                return self.parse_print_statement()
        elif self.current_tok.type == TokenType.IDENTIFIER:
            return self.parse_assignment()
        
        self.errors.append(f"Line {self.current_tok.line}: Syntax Error - Invalid statement start '{self.current_tok.value}'")
        self.advance()
        return None

    def parse_declaration(self):
        type_tok = self.current_tok
        self.advance() # int veya float'ı geç
        
        var_tok = self.expect(TokenType.IDENTIFIER)
        if not var_tok: return None
        
        # SEMANTİK KONTROL: Çift tanımlama var mı?
        if var_tok.value in self.declared_vars:
            self.errors.append(f"Line {var_tok.line}: Semantic Error - Duplicate declaration of variable '{var_tok.value}'")
        else:
            self.declared_vars[var_tok.value] = type_tok.value
            # Symbol Table'ı güncelle
            if var_tok.value in self.symbol_table:
                self.symbol_table[var_tok.value]['type'] = type_tok.value

        self.expect(TokenType.DELIMITER, ';')
        return VarDeclNode(type_tok, var_tok)

    def parse_assignment(self):
        var_tok = self.current_tok
        self.advance() # Identifier'ı geç
        
        # SEMANTİK KONTROL: Değişken önceden tanımlanmış mı?
        if var_tok.value not in self.declared_vars:
            self.errors.append(f"Line {var_tok.line}: Semantic Error - Undeclared variable '{var_tok.value}' used in assignment")

        if not self.expect(TokenType.OPERATOR, '='): return None
        
        expr = self.parse_expression()
        self.expect(TokenType.DELIMITER, ';')
        return VarAssignNode(var_tok, expr)

    def parse_print_statement(self):
        self.advance() # 'print'i geç
        self.expect(TokenType.DELIMITER, '(')
        expr = self.parse_expression()
        self.expect(TokenType.DELIMITER, ')')
        self.expect(TokenType.DELIMITER, ';')
        return PrintNode(expr)

    def parse_if_statement(self):
        self.advance() # 'if'i geç
        self.expect(TokenType.DELIMITER, '(')
        condition = self.parse_expression()
        self.expect(TokenType.DELIMITER, ')')
        
        self.expect(TokenType.DELIMITER, '{')
        if_body = []
        while self.current_tok.type != TokenType.EOF and not (self.current_tok.type == TokenType.DELIMITER and self.current_tok.value == '}'):
            stmt = self.parse_statement()
            if stmt: if_body.append(stmt)
        self.expect(TokenType.DELIMITER, '}')
        
        else_body = []
        if self.current_tok.type == TokenType.KEYWORD and self.current_tok.value == 'else':
            self.advance()
            self.expect(TokenType.DELIMITER, '{')
            while self.current_tok.type != TokenType.EOF and not (self.current_tok.type == TokenType.DELIMITER and self.current_tok.value == '}'):
                stmt = self.parse_statement()
                if stmt: else_body.append(stmt)
            self.expect(TokenType.DELIMITER, '}')
            
        return IfNode(condition, if_body, else_body)

    def parse_while_statement(self):
        self.advance() # 'while'ı geç
        self.expect(TokenType.DELIMITER, '(')
        condition = self.parse_expression()
        self.expect(TokenType.DELIMITER, ')')
        
        self.expect(TokenType.DELIMITER, '{')
        body = []
        while self.current_tok.type != TokenType.EOF and not (self.current_tok.type == TokenType.DELIMITER and self.current_tok.value == '}'):
            stmt = self.parse_statement()
            if stmt: body.append(stmt)
        self.expect(TokenType.DELIMITER, '}')
        return WhileNode(condition, body)

    def parse_expression(self):
        # En düşük öncelikli işlemler (Mantıksal ve Karşılaştırma operatörleri vb.) 
        # Proje kapsamını basit tutmak için arithmetic expression üzerinden gidiyoruz.
        left = self.parse_term()
        while self.current_tok.type == TokenType.OPERATOR and self.current_tok.value in ('+', '-', '>', '<', '==', '!=', '>=', '<='):
            op_tok = self.current_tok
            self.advance()
            right = self.parse_term()
            left = BinOpNode(left, op_tok, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_tok.type == TokenType.OPERATOR and self.current_tok.value in ('*', '/'):
            op_tok = self.current_tok
            self.advance()
            right = self.parse_factor()
            left = BinOpNode(left, op_tok, right)
        return left

    def parse_factor(self):
        tok = self.current_tok
        if tok.type in (TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL):
            self.advance()
            return NumberNode(tok)
        elif tok.type == TokenType.STRING_LITERAL:
            self.advance()
            return StringNode(tok)
        elif tok.type == TokenType.IDENTIFIER:
            # SEMANTİK KONTROL
            if tok.value not in self.declared_vars:
                self.errors.append(f"Line {tok.line}: Semantic Error - Undeclared variable '{tok.value}' used in expression")
            self.advance()
            return VarAccessNode(tok)
        elif tok.type == TokenType.DELIMITER and tok.value == '(':
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.DELIMITER, ')')
            return expr
            
        self.errors.append(f"Line {tok.line}: Syntax Error - Expected number, identifier or '('")
        self.advance()
        return None