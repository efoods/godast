from lib.generator import Generator
from lib.parser import Parser
from lib.reader import Reader
from lib.tokenizer import Tokenizer


class Analizer:
    reader = None
    tokenizer = None
    parser = None
    generator = None
    file_path = ''
    code_string = ''
    tokens = []
    ast = None

    def __init__(self, file_path, encoding):
        self.file_path = file_path
        self.reader = Reader(file_path, encoding)
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.generator = Generator()
        pass

    def read_code(self):
        self.reader.read()
        self.code_string = self.reader.get_content()
        return self

    def tokenlize(self):
        self.tokens = self.tokenizer.tokenlize(self.code_string).get_tokens()
        return self

    def paser(self):
        self.ast = self.parser.parse(self.tokens)
        return self

    def generate_code(self):
        return self.generator.generate_code(self.ast)
