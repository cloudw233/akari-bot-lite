import os

from core.exceptions import NoReportException
from core.builtins.message import MessageSession
from core.component import on_command

import subprocess

c = on_command('calc', developers=[
    'Dianliang233'], desc='安全地计算 Python ast 表达式。')


@c.handle('<math_expression>', options_desc={'+': '和/正数：1 + 2 -> 3',
                                             '-': '差/负数：3 - 1 -> 2',
                                             '/': '商：6 / 3 -> 2',
                                             '//': '整除：7 // 4 -> 1',
                                             '*': '积：2 * 3 -> 6',
                                             '**': 'x 的 y 次幂（由于性能问题，结果不得超过 4e+6）：2 ** 3 -> 8',
                                             '%': '取模：5 % 2 -> 1',
                                             '==': '等于：1 == 1 -> True',
                                             '<': '小于：1 < 2 -> True',
                                             '>': '大于：2 > 1 -> True',
                                             '<=': '小于等于：1 <= 2 -> True',
                                             '>>': 'x 右移 y 位（相当于 x / (2 ** y)，y < 10000）：32 >> 5 -> 1',
                                             '<<': 'x 左移 y 位（相当于 x * (2 ** y)，y < 10000）：1 << 5 -> 32',
                                             'in': 'x 在 y 中："hat" in "what" -> True',
                                             'not': '非：not True -> False',
                                             'is': 'x 与 y 是同一个对象：1 is 1 -> True',
                                             'randint(x)': '小于 x 的随机整数：randint(6) -> 5',
                                             'rand()': '0 与 1 之间的随机浮点数：rand() -> 0.5789015836448923',
                                             'int()': '转换为整数：int(1.5) -> 1',
                                             'float()': '转换为浮点数：float(1) -> 1.0',
                                             'str()': '转换为字符串：str(1) -> "1"',
                                             '更多数学函数': 'https://docs.python.org/zh-cn/3/library/math.html',
                                             '更多统计函数': 'https://docs.python.org/zh-cn/3/library/statistics.html',
                                             })
async def _(msg: MessageSession):
    try:
        res = subprocess.check_output(
            f'python {os.path.abspath("./modules/calc/calc.py")} {msg.parsed_msg["<math_expression>"]}'
            , timeout=10, shell=True)
        await msg.finish(f'{(msg.parsed_msg["<math_expression>"])} = {res.decode("utf-8")[:-1]}')
    except subprocess.TimeoutExpired:
        raise NoReportException('计算超时。')
    except Exception as e:
        raise NoReportException(e)
