# -*- coding: utf-8 -*-
import json
import time
from threading import Thread

RepeatTrue = True
Scoreboard = ''
TPS = 0
ScoreboardCount = 0

UUIDPath = 'server/usercache.json'
StatsPath = 'server/world/stats/'
PluginName = 'StatsRepeat'
ConfigFileFolder = 'config/'
ConfigFilePath = ConfigFileFolder + PluginName + '.json'
msg = """§d!!sr §r显示此条消息
§d!!sr start §r打开定时切换榜
§d!!sr stop §r关闭定时切换榜
§d!!sr set §r设置轮播切换时间（单位：秒）
§d!!sr reload §r初始化"""

#多线程
class StatsRepeat(Thread):
    def __init__(self,server):
        super().__init__()
        self.shutdown_flag = False
        self.server=server

    def run(self):
        global RepeatTrue
        global TPS
        #print('进入多线程')
        while not self.shutdown_flag:
            if self.shutdown_flag:
                return
            if RepeatTrue == True:
                Change(self.server)
                time.sleep(TPS)

    def shutdown(self):
        self.shutdown_flag = True
#切换榜单
def Change(server):
    global ScoreboardCount
    global Scoreboard
    ScoreboardCount = ScoreboardCount + 1
    if ScoreboardCount > len(Scoreboard):
        ScoreboardCount = 1
    server.execute('scoreboard objectives setdisplay sidebar ' + PluginName + str(ScoreboardCount)) 

#加载配置           
def loadconfig(server):
    global TPS
    global RepeatTrue
    global Scoreboard
    with open(ConfigFilePath,'r') as f:
        js = json.load(f)
    TPS = (js["Repeat"])
    RepeatTrue = js["Stats"]
    Scoreboard = js["Scoreboard"]

#读取UUID信息
def ReadUUID(server):
    global Cache
    Cache = {}
    with open(UUIDPath, 'r') as f:
        js = json.load(f)
    for i in js:
        Cache[i["name"]] = i["uuid"] 

#创建计分榜
def AddScoreboard(server,Criteria,Count):
    if len(Criteria.split( )) == 2:
        server.execute('scoreboard objectives add ' + PluginName + str(Count) + ' minecraft.' + str(Criteria).split( )[0] + ':minecraft.' + str(Criteria).split( )[1] + ' {"text":"§6' + Criteria.split( )[0] + '§e.' + Criteria.split( )[1] + '"}')
    else:
        server.execute('scoreboard objectives add ' + PluginName + str(Count) + ' minecraft.' + str(Criteria).split( )[0] + ':minecraft.' + str(Criteria).split( )[1] + ' {"text":"' + Criteria.split( )[2] + '"}')

#删除计分榜
def RemoveScoreboard(server,Criteria,Count):
    server.execute('scoreboard objectives remove ' + PluginName + str(Count))

#读取JSON并设置分数
def SetPoint(server,Criteria,Count):
    server.execute('save-all')
    global ScoreboardCount
    global Cache
    for i in Cache:
        with open(StatsPath + Cache[i] + '.json','r') as f:
            js = json.load(f)
        try:
            server.execute('scoreboard players set ' + i + ' ' + PluginName + str(Count) + ' ' + str(js["stats"]["minecraft:" + Criteria.split( )[0]]["minecraft:" + Criteria.split( )[1]]))
        except KeyError:
            None

#初始化计分榜
def initialize(server):
    global Scoreboard
    Count = 0
    for i in Scoreboard:
        Count = Count + 1
        RemoveScoreboard(server,i,Count) #移除
        AddScoreboard(server,i,Count) #创建
    #设置分数
    Count = 0
    for i in Scoreboard:
        Count = Count + 1
        SetPoint(server,Scoreboard[Count-1],Count)


def on_load(server, old):
    global StatsRepeat
    server.add_help_message('!!sr','查看插件StatsRepeat帮助') #添加帮助信息
    ReadUUID(server) #读取uuid信息
    loadconfig(server) #加载配置文件
    time.sleep(0.1) #稍微等一下服务器开启来
    initialize(server) #初始化

#多线程开启
    StatsRepeat = StatsRepeat(server)
    StatsRepeat.start()

def on_info(server, info):
    global Cache
    global RepeatTrue
    global TPS
    content = info.content
    if (content.split( )[0] == '!!sr') :
        if (len(content.split( )) == 1):
            server.say(msg)
        if len(content.split( )) == 2:
            if content.split( )[1] == 'start':
                RepeatTrue = True
                Change(server)
                server.say('已经榜单轮换已打开')
            else:
                if content.split( )[1] == 'stop':
                    RepeatTrue =False
                    server.execute('scoreboard objectives setdisplay sidebar')
                    server.say('已经榜单轮换已关闭')
                else:
                    if content.split( )[1] == 'reload':
                        server.say('正在加载配置')
                        loadconfig(server)
                    else:
                        server.say('参数错误，使用!!sr查看插件详情')
        if (len(content.split( )) == 3):
            if content.split( )[1] == 'set':
                if content.split( )[2].isdigit():
                    TPS = int(content.split( )[2])
                    server.say('设置转换时间为 ' + content.split( )[2]) 
                else:
                    server.say('参数错误，时间不能为非数字')
        if len(content.split( )) > 3:
            server.say('参数错误，使用!!sr查看插件详情')

def on_unload(server):
    global StatsRepeat
    StatsRepeat = StatsRepeat(server)
    StatsRepeat.shutdown()

def on_mcdr_stop(server):
    global StatsRepeat
    StatsRepeat = StatsRepeat(server)
    StatsRepeat.shutdown()