from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    UNKNOWN = auto()
    EOF = auto()
    

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Line {self.line}: {self.type.name} ('{self.value}')"