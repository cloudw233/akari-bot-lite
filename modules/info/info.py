from core.builtins import Bot
from core.component import on_command
from config import Config
from .server import server
import redis

inf = on_command('info', developers='haoye_qwq')
redis_ = str(Config('redis').split(':'))
db = redis.StrictRedis(host=redis_[0], port=int(redis_[1]), db=0)


# @inf.handle()
# async def inf_helps(msg: Bot.MessageSession):
#     inf = msg.options.get('command_alias')
#     if inf is None:
#         inf = {}
#     else:
#         if len(inf) == 0:
#             await msg.sendMessage('自定义命令别名列表为空。')
#         else:
#             send = await msg.sendMessage(Image(pir(
#                 f'[90秒后撤回消息]自定义命令别名列表：\n' + '\n'.join([f'{k} -> {inf[k]}' for k in inf]))))
#             await msg.sleep(90)
#             await send.delete()
#             await msg.finish()

@inf.handle('set <name> <ServerUrl> {添加服务器}', required_admin=True)
async def _(msg: Bot.MessageSession):
    group_id = msg.target.targetId
    name = msg.parsed_msg.get('<name>')
    db.set(f"{group_id}_{name}", msg.parsed_msg.get('<ServerUrl>'))
    db.setnx(f"{group_id}_list", [name])
    db.set(f"{group_id}_list", db.get(f"{group_id}_list").append(name), xx=True)
    await msg.sendMessage('添加成功')


@inf.handle('list {查看服务器列表}')
async def __(msg: Bot.MessageSession):
    group_id = msg.target.targetId
    if db.exists(f"{group_id}_list"):
        list_ = db.get(f"{group_id}_list")
        await msg.sendMessage('服务器列表:\n' + ', \n'.join(list_))
    else:
        await msg.sendMessage('列表中暂无服务器，请先绑定')


@inf.handle('url <ServerUrl> {查询任意服务器信息}')
async def ___(msg: Bot.MessageSession):
    info = await server(msg.parsed_msg.get('<ServerUrl>'))
    send = await msg.sendMessage(info + '[90秒后撤回]')
    send.sleep(90)
    send.delete()


@inf.handle('<name> {查询已绑定的服务器信息}')
async def ____(msg: Bot.MessageSession):
    name = msg.parsed_msg.get('<name>')
    group_id = msg.target.targetId
    if db.exists(f"{group_id}_{name}"):
        send = await msg.sendMessage(db.get(f"{group_id}_{name}") + '[90秒后撤回]')
        send.sleep(90)
        send.delete()
    else:
        send = await msg.sendMessage('服务器不存在，请检查输入\n[90秒后撤回]')
        send.sleep(90)
        send.delete()
