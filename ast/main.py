# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
from lib.analizer import Analizer


def callback():
    #print('this is callback')
    pass


def invoke(cb):
    cb()


def fun(name, *args, fbody='pass'):
    arls = list(args)
    fbs = fbody.split('\n')
    fstr = 'def ' + name + '(' + (','.join(arls)) + '):\n\t' + ('\t'.join(fbs)) + '\n'
    eval(fstr)

def main():
    # code_path = 'assert/index.js'
    code_path = 'lib/tokenizer.py'
    analizer = Analizer(code_path, 'UTF-8')
    analizer.read_code().tokenlize()
    # print(analizer.code_string)
    tokens = analizer.tokens
    for token in tokens:
        # if token['type'] == 'comment':
            print(token['type'] + '\t\t\t' + token['name'], end='\n')


main()
