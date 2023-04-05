from core.builtins import Bot
from core.component import on_command
from config import Config
from .server import server
from ast import literal_eval
import redis

inf = on_command('info', alias={'s': 'info url', 'server': 'info url'}, developers='haoye_qwq',
                 desc='Minecraft服务器信息模块')
redis_ = Config('redis').split(':')
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
    name = msg.parsed_msg['<name>'][0]
    db.set(f"{group_id}_{name}", msg.parsed_msg['<ServerUrl>'])
    if db.exists(f"{group_id}_list"):
        for i in db.get(f"{group_id}_list"):
            if i == name:
                break
            else:
                db.set(f"{group_id}_list", db.get(f"{group_id}_list").append(name))
                break
    else:
        db.set(f"{group_id}_list", [f"{name}"])
    await msg.sendMessage('添加成功')


@inf.handle('reset {重置服务器列表}')
async def _____(msg: Bot.MessageSession):
    group_id = msg.target.targetId
    db.delete(f"{group_id}_list")


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
    info = await server(msg.parsed_msg['<ServerUrl>'])
    send = await msg.sendMessage(info + '\n[90秒后撤回]')
    await msg.sleep(90)
    await send.delete()


@inf.handle('<name> {查询已绑定的服务器信息}')
async def ____(msg: Bot.MessageSession):
    name = msg.parsed_msg['<name>'][0]
    group_id = msg.target.targetId
    if db.exists(f"{group_id}_{name}"):
        info = await server(db.get(f"{group_id}_{name}"))
        send = await msg.sendMessage(str(info) + '\n[90秒后撤回]')
        await msg.sleep(90)
        await send.delete()
    else:
        send = await msg.sendMessage('服务器不存在，请检查输入\n[90秒后撤回]')
        await msg.sleep(90)
        await send.delete()
