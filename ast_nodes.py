class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self):
        return f"{self.token.value}"

class StringNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self):
        return f"{self.token.value}"

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
    def __repr__(self):
        return f"{self.var_name_tok.value}"

class VarDeclNode:
    def __init__(self, type_tok, var_name_tok):
        self.type_tok = type_tok
        self.var_name_tok = var_name_tok
    def __repr__(self):
        return f"(DECL {self.type_tok.value} {self.var_name_tok.value})"

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
    def __repr__(self):
        return f"({self.var_name_tok.value} = {self.value_node})"

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
    def __repr__(self):
        return f"({self.left_node} {self.op_tok.value} {self.right_node})"

class IfNode:
    def __init__(self, condition_node, if_body, else_body):
        self.condition_node = condition_node
        self.if_body = if_body
        self.else_body = else_body
    def __repr__(self):
        return f"(IF {self.condition_node} THEN {self.if_body} ELSE {self.else_body})"

class WhileNode:
    def __init__(self, condition_node, body):
        self.condition_node = condition_node
        self.body = body
    def __repr__(self):
        return f"(WHILE {self.condition_node} DO {self.body})"

class PrintNode:
    def __init__(self, expr_node):
        self.expr_node = expr_node
    def __repr__(self):
        return f"(PRINT {self.expr_node})"