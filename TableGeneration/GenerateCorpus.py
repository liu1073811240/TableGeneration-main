# -- coding: utf-8 --
# @Time : 2022/9/8 15:21
# @Author : Liu Hui
# @Email : 1073811240@qq.com
# @File : GenerateCorpus.py
# @Software: PyCharm

# 生成各大医院模板的语料
'''
1. 项目代码、项目编码  （MDFIEROLE、4562357457、S23453534SF34534）
2. 项目名称
3. 费用类别
4. 单位
5. 单价 （不能有整数）
6. 数量 （可以有整数）
7. 金额  （不能有整数）
8. 规格   （比如 10mg*24片/盒）
9. 自负比例   （30%、50%、100%）
10. 自负金额、自理金额
11. 医保类别  (甲类、乙类、丙类)

code、name、cost_clas、unit、unit-price、quantity、amount、specifications、conceit_ratio、self_financing_amount、
medical_insurance_category
'''

import random
import string
import numpy as np


class ProjectCode(object):
    lists_k = ['项目代码', '项目编码', '编号', '代码']

    def __init__(self):
        self.k = ['项目代码', '项目编码', '编号', '代码']

        # 值类似这种。
        # FINLER、MDFIEROLE、456235745b、S23453534SF34534、

    def __call__(self, *args, **kwargs):
        random_str = self.data_type()

        return random_str

    def data_type(self):
        number = random.choice([1, 2, 3, 4])
        # print(number)
        if number == 1:  # FINLER
            random_str = random.choices(string.ascii_uppercase, k=6)
        elif number == 2:  # MDFIEROLE
            random_str = random.choices(string.ascii_uppercase, k=9)
        elif number == 3:
            random_str = random.choices(string.digits, k=9)
            random_str.extend(random.choices(string.ascii_uppercase, k=1))
        elif number == 4:
            random_str = random.choices(string.ascii_uppercase, k=2)
            random_str.extend(random.choices(string.digits, k=13))
        else:
            random_str = random.choices(string.ascii_uppercase, k=6)
        # print(random_str)

        return ''.join(random_str)


class ProjectName(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        all_lists = self.load_name_dicts()

        random_str = random.choice(all_lists)

        return random_str

    def load_name_dicts(self):
        all_lists = []
        with open('./dicts/name_dictionary_v1.0.txt', 'r', encoding='utf-8') as f1:
            with open('./dicts/name_dictionary_v1.1.txt', 'r', encoding='utf-8') as f2:
                with open('./dicts/name_dictionary_v1.2.txt', 'r', encoding='utf-8') as f3:

                    lines1 = f1.readlines()
                    lines2 = f2.readlines()
                    lines3 = f3.readlines()

                    for line1 in lines1:
                        line1 = line1.strip('\n')
                        all_lists.append(line1)
                    for line2 in lines2:
                        line2 = line2.strip('\n')
                        all_lists.append(line2)
                    for line3 in lines3:
                        line3 = line3.strip('\n')
                        all_lists.append(line3)
                    # print(all_lists)

                f3.close()
            f2.close()
        f1.close()
        # print(all_lists)
        # print(len(all_lists))  # 44833

        return all_lists


class ProjectCostClas(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        all_lists = self.load_clas_dicts()
        random_str = random.choice(all_lists)

        return random_str

    def load_clas_dicts(self):
        all_lists = []
        with open('./dicts/费用类别语料.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip('\n')
                all_lists.append(line)
        return all_lists


class ProjectUnit(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        all_lists = self.load_unit_dicts()
        random_str = random.choice(all_lists)

        return random_str

    def load_unit_dicts(self):
        all_lists = []
        with open('./dicts/单位.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip('\n')
                all_lists.append(line)
        return all_lists


# 单价：0.89、1.11/12.11、500、
class ProjectUnitPrice(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        random_str = self.generate_price_rule()

        return random_str

    def generate_price_rule(self):
        p = np.array([0.8, 0.2])
        value = np.random.choice([8, 2], p=p.ravel())  # 指定概率取值

        if value == 8:
            random_str = self.price_rule1()
        else:
            random_str = self.price_rule2()

        return random_str

    def price_rule1(self):
        num = random.uniform(0, 100)
        num = round(num, 2)

        return str(num)

    def price_rule2(self):
        num = random.uniform(101, 1000)
        num = round(num, 2)

        return str(num)


# 数量：1.00 ~ 100.00
class ProjectQuantity(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        random_str = self.generate_quantity()

        return random_str

    def generate_quantity(self):
        num = random.uniform(0, 100)
        num = round(num, 2)

        return str(num)


class ProjectAmount(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        random_str = self.generate_amount()

        return random_str

    def generate_amount(self):
        num = random.uniform(0, 1000)
        num = round(num, 2)

        return str(num)


# 规格：
# ~ml    ml: 1 ~ 300
# ~ml/支   ml: 1 ~ 10
# ~ml/袋  ml: 100 ~ 1000
# ~mg/瓶  mg: 100 ~ 500
# ~mg/袋  mg: 1~100
# ~mg/1ml   mg: 0 ~ 1
# ~mg*~片/盒、  mg: 1 ~ 10  片：1 ~ 100
# ~mg*~支/支  mg: 1 ~ 10  支：1 ~ 5
# ~g*~片/盒、  g: 0 ~ 1  片：1 ~ 100
# ~g*~粒/盒、  g: 0 ~ 1  粒：1 ~ 100
# ~g/袋   g: 0 ~ 10
# ~g/支   g: 1 ~ 10
# ~g/kg  g: 100 ~ 1000
class Specifications(object):
    def __init__(self):
        self.dicts_spe = {'~ml': [1, 300], '~ml/支': [1, 10], '~ml/袋': [100, 1000], '~mg/瓶': [100, 500],
                          '~mg/袋': [1, 100], '~mg/1ml': [1, 2], '~mg*~片/盒': [[1, 10], [1, 100]],
                          '~mg*~支/支': [[1, 10], [1, 5]], '~g*~片/盒': [[1, 5], [1, 100]], '~g*~粒/盒': [[1, 10], [1, 100]],
                          '~g/袋': [1, 10], '~g/支': [1, 10], '~g/kg': [100, 1000], }

    def __call__(self, *args, **kwargs):
        out_l = self.generate_rule()
        random_str = random.choice(out_l)

        return random_str

    def generate_rule(self):
        out_l = []
        for k, v in self.dicts_spe.items():
            out_str = ''
            v_num = [s1 for s1 in k if s1 == '~']  # 判断'~'字符个数

            if len(v_num) == 1:  # 1个 ~
                for s2 in k:
                    if s2 == '~':
                        num = random.randint(v[0], v[1])
                        out_str += str(num)
                    else:
                        out_str += s2
                # print(out_str)

            elif len(v_num) == 2:  # '~mg*~片/盒': [[1, 10], [1, 100]],
                count = 0
                for s3 in k:
                    if s3 == '~' and count == 0:
                        num = random.randint(v[0][0], v[0][1])
                        out_str += str(num)
                        count += 1
                    elif s3 == '~' and count == 1:
                        num = random.randint(v[1][0], v[1][1])
                        out_str += str(num)
                        count += 1
                    else:
                        out_str += s3
                # print(out_str)

            else:
                out_str += ''
            out_l.append(out_str)

        return out_l


class ConceitRatio(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        out_l = self.generate_rule()
        random_str = random.choice(out_l)

        return random_str

    def generate_rule(self):
        out_l = ['30.00%', '50.00%', '100.00%']
        return out_l


class SelfFinancingAmount(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        random_str = self.generate_rule()

        return random_str

    def generate_rule(self):
        num = random.uniform(1, 500)
        num = round(num, 2)

        return str(num)

class MedicalInsuranceCategory():
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        category_l = self.generate_rule()
        random_str = random.choice(category_l)

        return random_str

    def generate_rule(self):
        category_l = ['甲类', '乙类', '丙类']

        return category_l


if __name__ == '__main__':
    # random_str = ProjectCode()()
    # ProjectName()()
    # all_lists = ProjectUnit()()
    # print(all_lists)
    # print(random_str)
    Specifications()()
