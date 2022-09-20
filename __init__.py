from hoshino import Service, priv
import os
try:
    import ujson as json
except:
    import json

sv_help = '''队友不及三人，快快寻找小伙伴吧～
- [招募队友 <留言>] 招募队友，并留言，如要求即性别、校区等
- [查询招募表] 		查看招募列表
- [取消招募队友] 	取消招募队友
'''.strip()

sv = Service('teamup', use_priv=priv.NORMAL, manage_priv=priv.ADMIN,
             visible=True, help_=sv_help, enable_on_default=False, bundle='查询')


@sv.on_fullmatch(["帮助招募队友"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


JSON_TEAM = (os.path.join(os.path.dirname(__file__), "teamup.json"))


async def render_forward_msg(msg_list: list, uids: list):
    forward_msg = []
    name = "招募员"
    for msg, uid in zip(msg_list, uids):
        forward_msg.append({
            "type": "node",
            "data": {
                "name": str(name),
                "uin": str(uid),
                "content": msg
            }
        })
    return forward_msg


def readfile():
    with open(JSON_TEAM, "r", encoding='utf8') as f:
        content = f.read()
        data = json.loads(content)
    return data


zhaomu = readfile()


def savefile():
    with open(JSON_TEAM, "w", encoding='utf8') as f:
        json.dump(zhaomu, f, ensure_ascii=False)


def add_message(gid, uid, message):
    if gid not in zhaomu:
        zhaomu[gid] = {}

    if uid not in zhaomu[gid]:
        zhaomu[gid][uid] = {}

    if message == "":
        message = "(这个人很懒，什么也没留下"

    zhaomu[gid][uid] = message

    savefile()


def delete_user(gid, uid):
    if gid not in zhaomu:
        return False

    if uid not in zhaomu[gid]:
        return False

    del zhaomu[gid][uid]

    savefile()

    return True


def process_table(gid):
    print(zhaomu)

    if gid not in zhaomu:
        return "招募表是空的哦qwq"

    msg = []
    qq = []
    for user, message in zhaomu[gid].items():
        msg.append(f"{user}: {message}")
        qq.append(user)

    if msg == []:
        msg = "招募表是空的哦qwq"

    return msg, qq


@sv.on_prefix('招募队友')
async def find_friend(bot, ev):

    gid = str(ev.group_id)
    uid = str(ev.user_id)

    if uid == "80000000":
        msg = "匿名你招募个🔨队友哦"
        await bot.send(ev, msg)
        return

    message = ev.message.extract_plain_text()

    add_message(gid, uid, message)

    msg = "成功添加至招募栏上～\n发送[查询招募表]可以查看别人的招募，有心仪的队伍速速联系对方Q号哦～\n招募成功了也请发送[取消招募队友]以便从招募公告中删除"

    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(('查看招募表', '查询招募表'))
async def query_table(bot, ev):

    gid = str(ev.group_id)

    msg, user = process_table(gid)

    if isinstance(msg, str):
        await bot.send(ev, msg)
    else:
        msg = await render_forward_msg(msg, user)
        await bot.send_group_forward_msg(group_id=ev.group_id, messages=msg)


@sv.on_fullmatch('取消招募队友')
async def cancle_zhaomu(bot, ev):

    gid = str(ev.group_id)
    uid = str(ev.user_id)

    if uid == "80000000":
        msg = "匿名你取消招募个🔨哦"
        await bot.send(ev, msg)
        return

    ok = delete_user(gid, uid)

    if ok:
        msg = "取消招募成功～"
    else:
        msg = "招募表没找你惹qwq是不是记错了？"

    await bot.send(ev, msg, at_sender=True)
