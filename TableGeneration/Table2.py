import random
import numpy as np
# from TableGeneration.GenerateCorpus import ProjectCode
from TableGeneration.GenerateCorpus import *

def load_courp(p, join_c=''):
    courp = []
    with open(p, mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip("\n").strip("\r\n")
            courp.append(line)
    courp = join_c.join(courp)
    return courp

def load_medicine_dicts():
    out_medicine_list = []
    with open('./dicts/name_dictionary_v1.0.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip('\n')
            out_medicine_list.append(line)

    return out_medicine_list


class Table:
    def __init__(self,
                 ch_dict_path,
                 en_dict_path,
                 cell_box_type='cell',
                 no_of_rows=14,
                 no_of_cols=14,
                 min_txt_len=2,
                 max_txt_len=7,
                 max_span_row_count=3,
                 max_span_col_count=3,
                 max_span_value=20,
                 color_prob=0,
                 cell_max_width=0,
                 cell_max_height=0):
        assert cell_box_type in [
            'cell', 'text'
        ], "cell_box_type must in ['cell', 'text'],cell: use cell location as cell box; text: use location of text in cell as cell box"
        self.cell_box_type = cell_box_type
        self.no_of_rows = no_of_rows
        self.no_of_cols = no_of_cols
        self.max_txt_len = max_txt_len
        self.min_txt_len = min_txt_len
        self.color_prob = color_prob
        self.cell_max_width = cell_max_width
        self.cell_max_height = cell_max_height
        self.max_span_row_count = max_span_row_count
        self.max_span_col_count = max_span_col_count
        self.max_span_value = max_span_value

        self.dict = ''
        self.ch = load_courp(ch_dict_path, '')
        self.en = load_courp(en_dict_path, '')  # "abcdefghijklmnopqrstuvwxyz"

        # print(self.ch)
        # print(self.en)

        self.medicine_lists = load_medicine_dicts()  # 载入药品字典
        # print(self.medicine_lists)

        # 边框风格
        self.pre_boder_style = {
            1: {
                'name': 'border',
                'style': {
                    'table': 'border:1px solid black;',
                    'td': 'border:1px solid black;font-family:NSimSun;',
                    'th': 'border:1px solid black;font-family:NSimSun;'
                }
            },  # 绘制全部边框
            2: {
                'name': 'border_top',
                'style': {
                    'table': 'border-top:1px solid black;',
                    'td': 'border-top:1px solid black;font-family:NSimSun',
                    'th': 'border-top:1px solid black;font-family:NSimSun'
                }
            },  # 绘制上横线
            3: {
                'name': 'border_bottom',
                'style': {
                    'table': 'border-bottom:1px solid black;',
                    'td': 'border-bottom:1px solid black;font-family:NSimSun',
                    'th': 'border-bottom:1px solid black;font-family:NSimSun'
                }
            },  # 绘制下横线
            4: {
                'name': 'head_border_bottom',
                'style': {
                    'th': 'border-bottom: 1px solid black;font-family:NSimSun'
                }
            },  # 绘制 head 下横线
            5: {
                'name': 'no_border',
                'style': {'td': 'font-family:NSimSun',
                          'th': 'font-family:NSimSun'}
            },  # 无边框
            6: {
                'name': 'border_left',
                'style': {
                    'table': 'border-left:1px solid black;',
                    'td': 'border-left:1px solid black;font-family:NSimSun',
                    'th': 'border-left:1px solid black;font-family:NSimSun'
                }
            },  # 绘制左竖线
            7: {
                'name': 'border_right',
                'style': {
                    'table': 'border-right:1px solid black;',
                    'td': 'border-right:1px solid black;font-family:NSimSun',
                    'th': 'border-right:1px solid black;font-family:NSimSun'
                }
            }  # 绘制右竖线
        }

        # 随机选择一种
        self.border_type = random.choice(list(self.pre_boder_style.keys()))
        # print(self.border_type)  # 1

        # self.border_type = 1

        self.spanflag = False
        '''cell_types matrix have two possible values:
            c: ch
            e: en
            n: number
            t: ''
            m: money
        '''
        self.cell_types = np.chararray(shape=(self.no_of_rows,
                                              self.no_of_cols))
        # print(self.cell_types)

        '''headers matrix have two possible values: 's' and 'h' where 'h' means header and 's' means simple text'''
        self.headers = np.chararray(shape=(self.no_of_rows, self.no_of_cols))
        # print(self.headers)

        '''A positive value at a position in matrix shows the number of columns to span and -1 will show to skip that cell as part of spanned cols'''
        self.col_spans_matrix = np.zeros(shape=(self.no_of_rows,
                                                self.no_of_cols))
        '''A positive value at a position means number of rows to span and -1 will show to skip that cell as part of spanned rows'''
        self.row_spans_matrix = np.zeros(shape=(self.no_of_rows,
                                                self.no_of_cols))
        '''missing_cells will contain a list of (row,column) pairs where each pair would show a cell where no text should be written'''
        self.missing_cells = []

        # print(self.col_spans_matrix)
        # print(self.row_spans_matrix)
        # print(self.missing_cells)

        # header_count will keep track of how many top rows and how many left columns are being considered as headers
        self.header_count = {'r': 2, 'c': 0}

    def get_log_value(self):
        ''' returns log base 2 (x)'''
        import math
        return int(math.log(self.no_of_rows * self.no_of_cols, 2))

    def define_col_types(self):
        '''
        We define the data type that will go in each column. We categorize data in three types:
        1. 'n': Numbers
        2. 'w': word
        3. 'r': other types (containing special characters)
        '''
        '''cell_types matrix have two possible values:
                    c: ch
                    e: en
                    n: number
                    t: ''
                    m: money
        '''

        prob_words = 0.3
        prob_numbers = 0.5
        prob_ens = 0.1
        prob_money = 0.1
        # print(self.cell_types)
        for i, type in enumerate(
                random.choices(
                    ['n', 'm', 'c', 'e'],
                    weights=[prob_numbers, prob_money, prob_words, prob_ens],
                    k=self.no_of_cols)):
            self.cell_types[:, i] = type
        # print('-----获取单元格类型------')
        # print(self.cell_types)

        '''The headers should be of type word'''
        self.cell_types[0:2, :] = 'c'
        # print(self.cell_types)
        # print('-----头部处理-----')

        '''All cells should have simple text but the headers'''
        self.headers[:] = 's'
        # print(self.headers)

        self.headers[0:2, :] = 'h'
        # print(self.headers)

    def define_col_types2(self):
        '''
        a - code、b - name、c - cost_clas、d - unit、e - unit-price、f - quantity、g - amount、h - specifications、
        i - conceit_ratio、j - self_financing_amount、k - medical_insurance_category

        '''
        cell_type_l = ['b', 'e', 'f', 'g']

        # prob_a = 0.2
        # prob_c = 0.2
        # prob_d = 0.2
        # prob_h = 0.1
        # prob_i = 0.1
        # prob_j = 0.1
        # prob_k = 0.1
        # cell_type_l2 = random.choices(
        #     ['a', 'c', 'd', 'h', 'i', 'j', 'k'],
        #     weights=[prob_a, prob_c, prob_d, prob_h, prob_i, prob_j, prob_k],
        #     k=self.no_of_cols - 4)
        cell_type_l2 = self.choice_cell_type()

        cell_type_l.extend(cell_type_l2)  # 添加其它单元格类型

        cell_type_l = self.sort_cell_type(cell_type_l)  # 排序 单元格类型

        for i, type in enumerate(cell_type_l):
            self.cell_types[:, i] = type

        self.headers[:] = 's'
        # print(self.no_of_rows, self.no_of_cols)
        # print(self.cell_types)
        # print(self.headers)

    def sort_cell_type(self, cell_type_l):
        # print(cell_type_l)
        random.shuffle(cell_type_l)
        # print(cell_type_l)
        out_l = []
        for cell_type in cell_type_l:
            if cell_type == 'b':
                out_l.insert(0, cell_type)
            else:
                out_l.append(cell_type)
        # print(out_l)
        return out_l

    def choice_cell_type(self):
        choice_l = ['a', 'c', 'd', 'h', 'i', 'j', 'k']
        if 0 < self.no_of_cols - 4 <= 7:
            out_l = random.sample(choice_l, self.no_of_cols - 4)
        else:
            out_l = []
        return out_l

    def generate_random_text(self, type):
        '''cell_types matrix have two possible values:
            c: ch
            e: en
            n: number
            t: ''
            m: money

        '''
        if type in ['n', 'm']:
            max_num = random.choice([10, 100, 1000, 10000])
            if random.random() < 0.5:
                out = '{:.2f}'.format(random.random() * max_num)
            elif random.random() < 0.7:
                out = '{:.0f}'.format(random.random() * max_num)
            else:
                # 随机保留小数点后2位
                out = str(random.random() *
                          max_num)[:len(str(max_num)) + random.randint(0, 3)]
            if type == 'm':
                out = '$' + out
        elif (type == 'e'):
            txt_len = random.randint(self.min_txt_len, self.max_txt_len)
            out = self.generate_text(txt_len, self.en)
            # 50% 的概率第一个字母大写
            if random.random() < 0.5:
                out[0] = out[0].upper()
        elif type == 't':
            out = ''
        else:
            txt_len = random.randint(self.min_txt_len, self.max_txt_len)
            out = self.generate_text(txt_len, self.ch)

        return ''.join(out)

    def generate_random_text2(self, type):
        '''
        a - code、b - name、c - cost_clas、d - unit、e - unit-price、f - quantity、g - amount、h - specifications、
        i - conceit_ratio、j - self_financing_amount、k - medical_insurance_category
        '''
        # print(type)
        if type == 'a':
            out = ProjectCode()()
        elif type == 'b':
            out = ProjectName()()
        elif type == 'c':
            out = ProjectCostClas()()
        elif type == 'd':
            out = ProjectUnit()()
        elif type == 'e':
            out = ProjectUnitPrice()()
        elif type == 'f':
            out = ProjectQuantity()()
        elif type == 'g':
            out = ProjectAmount()()
        elif type == 'h':
            out = ''
        elif type == 'i':
            out = ''
        elif type == 'j':
            out = ''
        elif type == 'k':
            out = ''
        elif type == 't':  # 置为空格
            out = ''
        else:
            out = ''
            print("出现其它单元格类型，已终止程序！！！")
            exit()

        # if type in ['n', 'm']:
        #     # max_num = random.choice([10, 100, 1000, 10000])
        #     # if random.random() < 0.5:
        #     #     out = '{:.2f}'.format(random.random() * max_num)
        #     # elif random.random() < 0.7:
        #     #     out = '{:.0f}'.format(random.random() * max_num)
        #     # else:
        #     #     # 随机保留小数点后2位
        #     #     out = str(random.random() *
        #     #               max_num)[:len(str(max_num)) + random.randint(0, 3)]
        #     # if type == 'm':
        #     #     out = '$' + out
        #     random_str = ProjectCode()()
        #     out = random_str
        # elif (type == 'e'):
        #     txt_len = random.randint(self.min_txt_len, self.max_txt_len)
        #     out = self.generate_text(txt_len, self.en)
        #
        #     # 50% 的概率第一个字母大写
        #     if random.random() < 0.5:
        #         out[0] = out[0].upper()
        # elif type == 't':
        #     out = ''
        # else:
        #     txt_len = random.randint(self.min_txt_len, self.max_txt_len)
        #     out = self.generate_text(txt_len, self.ch)
            # out = random.choice(self.medicine_lists)
        # print(type)  # e
        # print(out)  # ['B', 'o', 'u', 't', 'S', 't', 'o', 'r']
        return ''.join(out)

    def generate_text(self, txt_len, dict):
        random_star_idx = random.randint(0, len(dict) - txt_len)
        txt = dict[random_star_idx:random_star_idx + txt_len]
        return list(txt)

    def agnostic_span_indices(self, maxvalue, max_num=3):
        '''Spans indices. Can be used for row or col span
        Span indices store the starting indices of row or col spans while span_lengths will store
        the length of span (in terms of cells) starting from start index.'''
        # print(self.no_of_rows)
        # print(self.no_of_cols)
        # print(self.max_span_col_count)
        # print(maxvalue)
        # print(max_num)
        # print()
        # print("self.no_of_cols -> maxvalue -> ", self.no_of_cols)
        # print("self.max_span_col_count -> max_num -> ", self.max_span_col_count)

        span_indices = []
        span_lengths = []
        # random select span count
        span_count = random.randint(1, max_num)
        if (span_count >= maxvalue):  # 最大跨列单元格数 不能超过总的列数， 否则返回空列表
            return [], []

        indices = sorted(random.sample(list(range(0, maxvalue)), span_count))
        # print("indices:", indices)

        # get span start idx and span value
        starting_index = 0
        for i, index in enumerate(indices):
            # print(f'i: {i}, index: {index}')
            # print('starting_index:', starting_index)
            if (starting_index > index):
                continue

            max_lengths = maxvalue - index
            # print('max_lengths:', max_lengths)
            if (max_lengths < 2):  # 跨越单元格至少大于等于2
                break
            len_span = random.randint(1, min(max_lengths, self.max_span_value))  # 跨越单元格 的 格子数
            # print('len_span:', len_span)
            # print()

            if (len_span > 1):
                span_lengths.append(len_span)
                span_indices.append(index)
                starting_index = index + len_span
        # print('span_indices:', span_indices)
        # print('span_lengths:', span_lengths)

        return span_indices, span_lengths

    def make_first_row_spans(self):
        '''This function spans first row'''
        while (True):  # iterate until we get some first row span indices
            header_span_indices, header_span_lengths = self.agnostic_span_indices(
                self.no_of_cols, self.max_span_col_count)
            if (len(header_span_indices) != 0 and
                    len(header_span_lengths) != 0):
                break

        # print(self.col_spans_matrix)

        # make first row span matric
        row_span_indices = []
        for index, length in zip(header_span_indices, header_span_lengths):
            self.spanflag = True
            self.col_spans_matrix[0, index] = length
            self.col_spans_matrix[0, index + 1:index + length] = -1
            row_span_indices += list(range(index, index + length))

        # print("self.col_spans_matrix:\n", self.col_spans_matrix)
        # print("self.row_span_indices:", row_span_indices)

        # for not span cols, set it to row span value 2
        b = list(
            filter(lambda x: x not in row_span_indices,
                   list(range(self.no_of_cols))))
        # print("b:", b)

        self.row_spans_matrix[0, b] = 2
        self.row_spans_matrix[1, b] = -1
        # print("self.row_spans_matrix:\n", self.row_spans_matrix)

    def make_first_col_spans(self):
        '''To make some random row spans on first col of each row'''
        # print('---make_first_col_spans---')
        # print("self.row_spans_matrix:", self.row_spans_matrix)
        colnumber = 0
        # skip top 2 rows of header
        span_indices, span_lengths = self.agnostic_span_indices(
            self.no_of_rows - 2, self.max_span_row_count)

        span_indices = [x + 2 for x in span_indices]

        for index, length in zip(span_indices, span_lengths):
            self.spanflag = True
            self.row_spans_matrix[index, colnumber] = length
            self.row_spans_matrix[index + 1:index + length, colnumber] = -1

        # print("self.row_spans_matrix:", self.row_spans_matrix)
        # print("self.col_spans_matrix:", self.col_spans_matrix)
        # exit()

        # print(self.headers)
        # self.headers[:, colnumber] = 'h'
        # print(self.headers)
        # print(self.header_count)
        # self.header_count['c'] += 1
        # print(self.header_count)
        # exit()

    def generate_missing_cells(self):
        '''This is randomly select some cells to be empty (not containing any text)'''
        # print(self.get_log_value())
        missing = np.random.random(size=(self.get_log_value(), 2))
        # print("missing:\n", missing)
        # print("no_of_rows:", self.no_of_rows)
        # print("self.no_of_cols:", self.no_of_cols)
        # print("self.header_count:", self.header_count)

        missing[:, 0] = (self.no_of_rows - 1 - self.header_count['r']
                         ) * missing[:, 0] + self.header_count['r']
        missing[:, 1] = (self.no_of_rows - 1 - self.header_count['c']
                         ) * missing[:, 1] + self.header_count['c']
        # print(self.cell_types)
        # print("missing:\n", missing)

        for arr in missing:
            self.missing_cells.append((int(arr[0]), int(arr[1])))
        # print(self.missing_cells)

    def create_style(self):
        '''This function will dynamically create stylesheet. This stylesheet essentially creates our specific
        border types in tables'''
        boder_style = self.pre_boder_style[self.border_type]['style']
        # print(boder_style)

        style = '<head><meta charset="UTF-8"><style>'
        style += "html{background-color: white;}table{"

        # 表格中文本左右对齐方式
        style += "text-align:{};".format(
            random.choices(
                ['left', 'right', 'center'], weights=[0.25, 0.25, 0.5])[0])
        style += "border-collapse:collapse;"
        if 'table' in boder_style:
            style += boder_style['table']
        style += "}td{"

        # 文本上下居中
        if random.random() < 0.5:  # 0.5
            style += "align: center;valign: middle;"
        # 大单元格
        if self.cell_max_height != 0:
            style += "height: {}px;".format(
                random.randint(self.cell_max_height // 2,
                               self.cell_max_height))
        if self.cell_max_width != 0:
            style += "width: {}px;".format(
                random.randint(self.cell_max_width // 2, self.cell_max_width))

        # print(style)
        # print(boder_style)

        # 文本换行
        style += "word-break:break-all;"
        if 'td' in boder_style:
            style += boder_style['td']

        style += "}th{padding:6px;padding-left: 15px;padding-right: 15px;"
        if 'th' in boder_style:
            style += boder_style['th']
        style += '}'

        style += "</style></head>"
        return style

    def create_html(self):
        '''Depending on various conditions e.g. columns spanned, rows spanned, data types of columns,
        regular or irregular headers, tables types and border types, this function creates equivalent html
        script'''
        idcounter = 0
        structure = []
        temparr = ['td', 'th']
        html = """<html>"""
        html += self.create_style()
        html += '<body><table>'
        # html += '<table style="width: 100%; table-layout:fixed;">'
        print("self.cell_types:\n", self.cell_types)
        print("self.row_spans_matrix:\n", self.row_spans_matrix)
        print("self.col_spans_matrix:\n", self.col_spans_matrix)
        print("self.headers:\n", self.headers)
        print("self.missing_cells:\n", self.missing_cells)
        print("html:", html)
        print("structure:", structure)
        print("self.no_of_rows:", self.no_of_rows)
        print("self.no_of_cols:", self.no_of_cols)

        for r in range(self.no_of_rows):
            html += '<tr>'
            structure.append('<tr>')
            for c in range(self.no_of_cols):
                text_type = self.cell_types[r, c].decode('utf-8')
                # print('text_type:', text_type)  # c/e/n/t/m  ch/en/number/''/money

                row_span_value = int(self.row_spans_matrix[r, c])
                col_span_value = int(self.col_spans_matrix[r, c])
                htmlcol = temparr[['s', 'h'].index(self.headers[r][c].decode(
                    'utf-8'))]  # th / td

                # print("htmlcol:", htmlcol)  # th 或 td

                if self.cell_box_type == 'cell':
                    htmlcol += ' id={}'.format(idcounter)

                # print(htmlcol)  # th id=0
                htmlcol_style = htmlcol
                # set color
                if (col_span_value != 0) or (r, c) not in self.missing_cells:
                    if random.random() < self.color_prob:
                        color = (random.randint(200, 255), random.randint(
                            200, 255), random.randint(200, 255))
                        htmlcol_style += ' style="background-color: rgba({}, {}, {},1);"'.format(
                            color[0], color[1], color[2])

                if (row_span_value == -1):
                    continue

                elif (row_span_value > 0):
                    html += '<' + htmlcol_style + ' rowspan=\"' + str(
                        row_span_value) + '">'
                    if row_span_value > 1:
                        structure.append('<td')
                        structure.append(' rowspan=\"{}\"'.format(
                            row_span_value))
                        structure.append('>')
                    else:
                        structure.append('<td>')
                else:  # 在横列 为 0 的情况下
                    if (col_span_value == 0):
                        if (r, c) in self.missing_cells:
                            text_type = 't'
                    if (col_span_value == -1):
                        continue
                    html += '<' + htmlcol_style + ' colspan=\"' + str(
                        col_span_value) + '">'
                    if col_span_value > 1:
                        structure.append('<td')
                        structure.append(' colspan=\"{}\"'.format(
                            col_span_value))
                        structure.append('>')
                    else:
                        structure.append('<td>')
                # if c == 0:
                    # 第一行设置为中英文
                    # text_type = random.choice(['c', 'e'])

                # print("text_type:", text_type)

                # txt = self.generate_random_text(text_type)
                txt = self.generate_random_text2(text_type)
                # print("txt:", txt)
                if self.cell_box_type == 'text':
                    txt = '<span id=' + str(idcounter) + '>' + txt + ' </span>'

                # print("txt:", txt)
                idcounter += 1
                html += txt + '</' + htmlcol + '>'
                # print(html)

                structure.append('</td>')

            html += '</tr>'
            structure.append('</tr>')
        html += "<table></body></html>"
        # print(html)
        # print(structure)
        # print(idcounter)

        return html, structure, idcounter

    def create(self):
        '''This will create the complete table'''
        # self.define_col_types()  # define the data types for each column
        self.define_col_types2()
        # print(self.cell_types)
        # print(self.headers)

        self.generate_missing_cells()  # generate missing cells
        # print("填充单元格为缺失", self.missing_cells)

        # print("边界类型：", self.border_type)
        # print(self.row_spans_matrix)
        # print(self.col_spans_matrix)

        if self.border_type < 60:  # 绘制横线的情况下进行随机span
            # first row span
            if self.max_span_col_count > 0:
                self.make_first_row_spans()
            # first col span
            if random.random() < 1 and self.max_span_row_count > 0:
                self.make_first_col_spans()
        # print(self.cell_types)
        # print(self.headers)
        # print(self.row_spans_matrix)
        # print(self.col_spans_matrix)
        # print(self.missing_cells)

        html, structure, idcounter = self.create_html(
        )  # create equivalent html
        # print("html:", html)
        # print("structure:", structure)
        # print("idcounter:", idcounter)

        return idcounter, html, structure, self.pre_boder_style[
            self.border_type]['name']
