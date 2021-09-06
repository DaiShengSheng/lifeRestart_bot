# coding=utf-8
from hoshino import Service
from hoshino.typing import HoshinoBot,CQEvent
from .Life import Life
from .PicClass import *
import traceback
import time
import random

sv = Service("人生重来模拟器")

def genp(prop):
    ps = []
    # for _ in range(4):
    #     ps.append(min(prop, 8))
    #     prop -= ps[-1]
    tmp = prop
    while True:
        for i in range(0,4):
            if i == 3:
                ps.append(tmp)
            else:
                if tmp>=10:
                    ps.append(random.randint(0, 10))
                else:
                    ps.append(random.randint(0, tmp))
                tmp -= ps[-1]
        if ps[3]<10:
            break
        else:
            tmp = prop
            ps.clear()
    return {
        'CHR': ps[0],
        'INT': ps[1],
        'STR': ps[2],
        'MNY': ps[3]
    }

@sv.on_fullmatch(("/remake","人生重来"))
async def remake(bot,ev:CQEvent):
    pic_list = []
    mes_list = []

    Life.load(FILE_PATH+'\data')
    while True:
        life = Life()
        life.setErrorHandler(lambda e: traceback.print_exc())
        life.setTalentHandler(lambda ts: random.choice(ts).id)
        life.setPropertyhandler(genp)
        flag = life.choose()
        if flag:
            break

    choice = 0
    person = ev["sender"]["nickname"] + "本次重生的基本信息如下：\n\n【你的天赋】\n"
    for t in life.talent.talents:
        choice = choice + 1
        person = person + str(choice) + "、天赋：【" + t.name + "】" + " 效果:" + t.desc + "\n"

    person = person + "\n【基础属性】\n"
    person = person + "   美貌值:" + str(life.property.CHR)+"  "
    person = person + "智力值:" + str(life.property.INT)+"  "
    person = person + "体质值:" + str(life.property.STR)+"  "
    person = person + "财富值:" + str(life.property.MNY)+"  "
    pic_list.append("这是"+ev["sender"]["nickname"]+"本次轮回的基础属性和天赋:")
    pic_list.append(ImgText(person).draw_text())

    await bot.send(ev, "你的命运正在重启....",at_sender=True)
    time.sleep(5)

    res = life.run() #命运之轮开始转动
    mes = '\n'.join('\n'.join(x) for x in res)
    pic_list.append("这是"+ev["sender"]["nickname"]+"本次轮回的生平:")
    pic_list.append(ImgText(mes).draw_text())

    sum = life.property.gensummary() #你的命运之轮到头了
    pic_list.append("这是" + ev["sender"]["nickname"] + "本次轮回的评价:")
    pic_list.append(ImgText(sum).draw_text())

    for img in pic_list:
        data = {
            "type": "node",
            "data": {
                "name": "色图机器人",
                "uin": "2854196310",
                "content": img
            }
        }
        mes_list.append(data)

    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_list)
