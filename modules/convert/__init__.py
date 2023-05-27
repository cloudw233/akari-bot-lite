import os
import pint
from decimal import Decimal


from core.builtins import Bot
from core.component import module
from core.exceptions import NoReportException

# ureg = UnitRegistry(os.path.dirname(os.path.abspath(__file__)) +
#                     '/default_bi_zh-cn_en.txt', non_int_type=Decimal)
ureg = UnitRegistry(non_int_type=Decimal)
i = module('convert', alias=('conv', 'unit'), desc='{convert.help.desc}',
           developers=['Dianliang233'], support_languages=['en_us'])


@i.command('<from_val> <to_unit> {convert.help}')
async def _(msg: Bot.MessageSession):
    from_val = msg.parsed_msg['<from_val>']
    to_unit = msg.parsed_msg['<to_unit>']
    try:
        ori = ureg.parse_expression(from_val)
        res = ureg.parse_expression(from_val).to(to_unit)
        await msg.finish(f"{ori:~Pg} = {res:~Pg}")
    except UndefinedUnitError:
        return msg.locale.t("convert.message.error.invalid_unit") 
    except DimensionalityError:
        return msg.locale.t("convert.message.error.cannot_convert") 