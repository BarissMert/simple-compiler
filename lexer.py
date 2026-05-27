import re
from tokens import Token, TokenType

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.symbol_table = {}
        self.errors = []
        
        # Dilin sözdizimi kurallarını Regex olarak tanımlıyoruz (Öncelik sırası önemlidir)
        self.token_specification = [
            ('FLOAT_LITERAL',   r'\d+\.\d+'),                              # Örn: 3.14
            ('INTEGER_LITERAL', r'\d+'),                                   # Örn: 42
            ('STRING_LITERAL',  r'".*?"'),                                 # Örn: "Result is large"
            ('OPERATOR',        r'==|!=|<=|>=|&&|\|\||[+\-*/=><]'),        # Çift ve tek karakterli operatörler
            ('DELIMITER',       r'[;{}()]'),                               # Noktalı virgül ve parantezler
            ('IDENTIFIER',      r'[A-Za-z_][A-Za-z0-9_]*'),                # Değişken isimleri
            ('WHITESPACE',      r'[ \t]+'),                                # Boşluklar (atlanacak)
            ('NEWLINE',         r'\n'),                                    # Satır sonları (satır sayısını artırmak için)
            ('UNKNOWN',         r'.'),                                     # Eşleşmeyen hatalı karakterler
        ]
        
        # Tüm kuralları tek bir Regex deseninde birleştiriyoruz
        self.tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        
        # Dilin anahtar kelimeleri
        self.keywords = {'int', 'float', 'if', 'else', 'while', 'print'}

    def tokenize(self):
        line_num = 1
        # finditer, eşleşen tüm kısımları sırayla döndürür
        for mo in re.finditer(self.tok_regex, self.source_code):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == 'NEWLINE':
                line_num += 1
                continue
            elif kind == 'WHITESPACE':
                continue
            elif kind == 'UNKNOWN':
                self.errors.append(f"Line {line_num}: Lexical Error - Invalid character '{value}'")
                continue
            elif kind == 'IDENTIFIER' and value in self.keywords:
                kind = 'KEYWORD'
            
            # Token nesnesini oluştur ve listeye ekle
            token_enum = getattr(TokenType, kind)
            self.tokens.append(Token(token_enum, value, line_num))
            
            # Eğer bir IDENTIFIER ise ve sembol tablosunda yoksa ekle
            if kind == 'IDENTIFIER' and value not in self.symbol_table:
                self.symbol_table[value] = {
                    'type': None,           # Parser aşamasında doldurulacak
                    'scope': 'global', 
                    'line_declared': line_num
                }
                
        self.tokens.append(Token(TokenType.EOF, 'EOF', line_num))
        return self.tokens, self.symbol_table, self.errors