class Reader:
    __content = ''
    __filepath = ''
    __encoding = 'UTF-8'

    def __init__(self, path, encoding='UTF-8'):
        self.__filepath = path
        self.__encoding = encoding

    def read(self):
        f = open(self.__filepath, encoding=self.__encoding)
        self.__content = f.read()

    def get_content(self):
        return self.__content
