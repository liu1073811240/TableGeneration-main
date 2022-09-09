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


if __name__ == '__main__':

    random_str = ProjectCode()()
    # print(random_str)



