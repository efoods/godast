import re
import json
import sys
from lib.reader import Reader


class Tokenizer:
    # 源代码
    __code_string = ''
    # 分词数组
    __tokens = []
    # 表示符 和关键字
    __word = ''
    # 过程变量 符号组 匹配多符号操作符分词使用
    __compose_punctuation = ''
    # 预定的多符号操作符分词
    __multi_operators = []
    # 字符串
    __str_start = False
    __str_start_flag = ''
    __str_end_flag = ''
    __string = ''
    __string_type = ''
    # 注释
    __comment_start = False
    __comment_string = ''
    __comment_start_flag = ''
    __comment_end_flag = ''
    __comment_type = ''
    # 配置
    __config = None
    # 临时
    __temp = ''

    def __init__(self, config_path=".\\config\\tokens.json"):
        self.__config = json.load(open(config_path))
        self.__init_multi_operators()

    def __init_multi_operators(self):
        markers = self.__config["markers"];
        keys = [marker
                for marker in markers
                if marker != "all-punctuations"]
        slots = []
        for key in keys:
            slots += [markers[key][i]
                      for i in range(len(markers[key]))
                      if len(markers[key][i]) != 1]
        slots.sort(key=lambda i: len(i), reverse=True)
        self.__multi_operators = slots

    def tokenlize(self, code_string):
        self.__code_string = code_string
        self.__tokenlize()
        return self

    def __tokenlize(self):
        cr = 0
        cc = -1
        sr = 0
        sc = 0
        for i in range(len(self.__code_string)):
            c = self.__code_string[i]
            cc += 1
            # 文件结束
            # 注释单元
            if self.__comment_start:
                if self.__comment_string == '':
                    sr = cr
                    sc = cc
                self.handle_comment(c, (sr, sc, cr, cc))
            # 字符串单元
            elif self.__str_start:
                if self.__string == '':
                    sr = cr
                    sc = cc
                self.handle_string(c, (sr, sc, cr, cc))
            elif self.is_string(c):
                self.stop_last_handle((sr, sc, cr, cc))
                if not self.__comment_start:
                    self.str_parse_start(c)
                else:
                    self.handle_comment(c, (sr, sc, cr, cc))
                continue
            elif self.is_comment(c):
                self.stop_last_handle((sr, sc, cr, cc))
                if not self.__str_start:
                    self.comment_parse_start(c)
                else:
                    self.handle_string(c, (sr, sc, cr, cc))
                continue
            # 词法单元
            else:
                # 换行符
                if self.is_line_end(c):
                    self.stop_last_handle((sr, sc, cr, cc))
                    cr += 1
                    cc = -1
                    if self.__comment_start:
                        self.handle_comment(c, (sr, sc, cr, cc))
                        continue
                # 空白
                elif self.is_blank(c):
                    self.stop_last_handle((sr, sc, cr, cc))
                    cr += 1
                    cc = -1
                    if self.__comment_start:
                        self.handle_comment(c, (sr, sc, cr, cc))
                        continue
                # 分隔符
                elif self.is_separater(c):
                    self.stop_last_handle((sr, sc, cr, cc))
                    self.handle_separater(c, (cr, cc, cr, cc))
                # 字母,数字,_,$
                elif self.is_alpha(c):
                    if self.__word == '':
                        self.stop_last_handle((sr, sc, cr, cc))
                        sr = cr
                        sc = cc
                        if self.__comment_start:
                            self.handle_comment(c, (sr, sc, cr, cc))
                            continue
                    self.__word += c
                # 标点和运算符
                elif self.is_punctuation(c):
                    if self.__compose_punctuation == '':
                        self.stop_last_handle((sr, sc, cr, cc))
                        sr = cr
                        sc = cc
                    self.__compose_punctuation += c
                else:
                    self.stop_last_handle((sr, sc, cr, cc))
        if self.__comment_start:
            self.__comment_string += self.__temp
            self.__temp = self.__comment_end_flag[:-1]
            self.handle_comment(self.__comment_end_flag[-1], (sr, sc, cr, cc))
        if self.__str_start:
            self.handle_string(self.__str_end_flag, (sr, sc, cr, cc))
        self.stop_last_handle((sr, sc, cr, cc))

    def is_line_end(self, c):
        return c == '\n'

    def is_blank(self, c):
        return re.match(r'\s', c)

    def is_punctuation(self, c):
        return re.match(r'[~`!@#$%^&*()_\-+={}\[\]|\\:;"\'<>,\.?\/]', c)

    def is_separater(self, c):
        return re.match(r'[,;]', c)

    def is_operator(self, c):
        return re.match(r'[+\-\*%~!^&=\|]', c)

    def is_alpha(self, c):
        return re.match(r'[\w_$]', c)

    def is_string(self, marker):
        # if self.__comment_start:
        #     return False
        rules = self.__config['strings']
        for rule in rules:
            if rule['start'] == marker:
                self.__str_start_flag = rule['start']
                self.__str_end_flag = rule['end']
                return True
        return False

    def is_string_end(self, c):
        if self.__str_end_flag == c:
            tmp = self.__string[-1::-1]
            res = re.search(r'[\\]*',tmp)
            if res != None:
                 if len(res.group(0)) % 2 == 0:
                     return True
        return False
        #     cn = 0
        #     for i in tmp:
        #         if i == '\\':
        #             cn += 1
        #         else:
        #             break
        #     if cn % 2 == 0:
        #         return True
        # return False



    def str_parse_start(self, marker):
        self.__str_start = True
        self.__string += marker

    def is_comment(self, marker):
        rules = self.__config['comments']
        for rule in rules:
            if rule['start'] == marker:
                self.__comment_start_flag = rule['start']
                self.__comment_end_flag = rule['end']
                return True
        return False

    def comment_parse_start(self, marker):
        self.__comment_start = True
        self.__comment_string += marker

    def is_keyword(self, word):
        keywords = self.__config['keywords']
        for kw in keywords:
            if word == kw:
                return True
        return False

    def is_number(self, word):
        return re.match(r'\d$', word)

    def handle_comment(self, c, pos):
        self.__temp += c
        if len(self.__temp) == len(self.__comment_end_flag):
            # 相等则检测出字符串结尾标志 说明字符串已经结束
            if self.__temp == self.__comment_end_flag:
                if self.__comment_end_flag != '\n':
                    self.__comment_string += self.__temp
                self.apped_tokens('comment', self.__comment_string, pos)
                self.__comment_string = ''
                self.__comment_start = False
                self.__comment_start_flag = ''
                self.__comment_end_flag = ''
                self.__temp = ''
            else:
                self.__comment_string += self.__temp[0]
                self.__temp = self.__temp[1:]
        elif len(self.__temp) < len(self.__comment_end_flag):
            pass
        pass

    def handle_string(self, c, pos):
        # self.__temp += c
        # if len(self.__temp) == len(self.__str_end_flag):
            # 相等则检测出字符串结尾标志 说明字符串已经结束
            tmp = self.__string
            tmp = tmp.replace('\\\\', '\\')
            if self.is_string_end(c):
                self.__string += c
                self.apped_tokens('string', self.__string, pos)
                self.__string = ''
                self.__str_start = False
                self.__str_end_flag = ''
                self.__str_start_flag = ''
                # self.__temp = ''
            else:
                self.__string += c
                # self.__temp = self.__temp[1:]
        # elif len(self.__temp) < len(self.__str_end_flag):
        #     pass
        # pass

    def handle_separater(self, c, pos):
        self.apped_tokens('separater', c, pos)

    def handle_punctuation(self, pos):
        if self.__compose_punctuation:
            markers = self.__multi_operators
            chars = self.__compose_punctuation
            self.__compose_punctuation = ''
            sr = pos[0]
            sc = pos[1]
            cr = pos[0]
            cc = pos[1]
            while len(chars) != 0:
                matched = False
                for marker in markers:
                    if chars.startswith(marker):
                        matched = True
                        cc += len(marker)
                        chars = chars[len(marker):]
                        if self.is_comment(marker):
                            self.comment_parse_start(marker)
                            clen = len(chars)
                            # i = 0
                            while  clen > 0:
                                self.handle_comment(chars[0], (sr, sc, cr, cc))
                                chars = chars[1:]
                                clen = len(chars)
                                cc += 1
                                if not self.__comment_start:
                                    break
                        else:
                            self.apped_tokens('operator', marker, (sr, sc, cr, cc))
                        sc = cc
                        break
                if self.__comment_start:
                    break
                if not matched:
                    cc += 1
                    self.apped_tokens('operator', chars[0], (sr, sc, cr, cc))
                    chars = chars[1:]
                    sc = cc

    def handle_word(self, pos):
        if self.__word:
            if self.is_keyword(self.__word):
                self.apped_tokens('keyword', self.__word, pos)
            elif self.is_number(self.__word):
                self.apped_tokens('number', self.__word, pos)
            else:
                self.apped_tokens('identifier', self.__word, pos)
            self.__word = ''

    def stop_last_handle(self, pos):
        self.handle_word(pos)
        self.handle_punctuation(pos)

    def apped_tokens(self, t_type, name, pos):
        self.__tokens.append({
            'type': t_type,
            'name': name,
            'pos': {
                'start_row': pos[0],
                'start_col': pos[1],
                'end_row': pos[2],
                'end_col': pos[3]
            },
            'org': name
        })

    def get_tokens(self):
        return self.__tokens
