import requests
import json
from bs4 import BeautifulSoup
import os

BASELINK = 'http://music.baidu.com'
PLAYLINK = 'http://play.baidu.com'
INFOLINK = '/data/music/songinfo'
SONGLINK = '/data/music/songlink'

TOPLINK = [{'Name':'1-新歌榜','Link':'/top/new'},
           {'Name':'2-热歌榜','Link':'/top/hot'},
           {'Name':'3-老歌榜','Link':'/top/oldsong'},
           {'Name':'4-网歌榜','Link':'/top/netsong'},
           {'Name':'5-原创榜','Link':'/top/song'},
           {'Name':'6-搜歌','Link':'xxx'},
           {'Name':'7-退出','Link':'exit()'}]


def ShowMenu(menu):
    print('='*10)
    #循环取值
    for item in menu:
        print(item['Name'])
    print('='*10)

    #获取输入值
    menuSelect = input('请输入选择值>>>>:')

    if menuSelect == '7': exit()
    #判断选择值
    return menuSelect if int(menuSelect) < len(menu) and int(menuSelect) > 0 else ShowMenu(menu)

def ret3List(pageStr):
    list = []
    if '-' in pageStr:
        x1 = int(str(pageStr).split('-')[0])
        x2 = int(str(pageStr).split('-')[1])
        while x1 <= x2:
            list.append(x1)
            x1 += 1
    elif ',' in pageStr:
        list = str(pageStr).split(',')
    else:
        list.append(int(pageStr))
    return ','.join(list)

def downFile(downlist):
    save_path = os.path.dirname(os.path.abspath(__file__)) + '/mp3/'
    for item in downlist:
        with open(save_path + item['Name'] + '.mp3', 'wb') as f:
            f.write(requests.get(item['Link']).content)
        f.close()
        print(item['Name'] + '已下载完毕')


class MusicList:

    @staticmethod
    def getListDown(liststring,httplink):
        list = liststring.split(',')
        downList = []
        for item in list:
            #通过歌曲编号，获取每支歌的名字与下载链接，同样使用json
            data = {'songIds':item}
            datastr = requests.post(httplink,data=data)
            soup = BeautifulSoup(datastr.content)
            #必须要用.text，否则就带上<body>头尾了
            bodytext = soup.find('body').text
            bodyjson = json.loads(bodytext)
            Name = bodyjson['data']['songList'][0]['songName']
            Link = bodyjson['data']['songList'][0]['songLink']
            #形成字典
            downList.append({'Name':Name,'Link':Link})
        return downList


    @staticmethod
    def sendHttp(httplink,pageNo=1,size=20,third_type=0):
        startNo = int(size) * (int(pageNo)-1)
        linkstr = '?start=' + str(startNo) +'&size=' + str(size) +'&third_type=' + str(third_type)

        data = requests.get(httplink +'/?pst=shouyeTop') if pageNo==1 else requests.get(httplink + linkstr)
        soup = BeautifulSoup(data.content)
        #寻找所有span class="music-icon-hook"以定位
        return soup

    @staticmethod
    def soup2list(soup):
        musicList = soup.find_all('span',attrs={'class':'music-icon-hook'})
        #列出所有歌曲的id
        list = []
        for item in musicList:
            #有null值，所以无法用eval转成字典，只能用json.loads转
            list.append(json.loads(item['data-musicicon'])['id'])
            # list.append(str(item['data-musicicon']['id']))
        return ','.join(list)

    @staticmethod
    def getDownPages(soup):
        pageNode = soup.find('a',attrs={'class':'page-navigator-number 		PNNW-S'})
        pageNode = pageNode.previous_sibling


        pageCount = pageNode.string
        sizeCount = (str(pageNode['href']).split('size=')[1]).split('&')[0]

        #提示下载页码编码
        pageSelect = input('总页数是%s,请输入下载编号【2-4】或3，5:'%pageCount)

        return pageSelect,sizeCount



if __name__ == '__main__':
    #询问清单要求
    ret1 = ShowMenu(TOPLINK)
    #获取首次链接，并获取总页数与单页数量
    ret2 = MusicList.sendHttp(BASELINK + TOPLINK[int(ret1)-1]['Link'],1,0,0)
    #获取需要下载的总页码和页码,以及单页数
    ret3,size = MusicList.getDownPages(ret2)
    #循环以下载
    ret4 = str(ret3List(ret3)).split(',')
    for item in ret4:
        ret5 = MusicList.sendHttp(BASELINK + TOPLINK[int(ret1)-1]['Link'],int(item),int(size),0)
        ret6 = MusicList.soup2list(ret5)
        ret7 = MusicList.getListDown(ret6,(PLAYLINK + SONGLINK))
        ret8 = downFile(ret7)



# url='http://play.baidu.com/data/music/songlink'
# data={'songIds':'790142'}
# r=requests.post(url,data=data)
# print (r.content.decode('UTF-8'))
# f=open('data.txt','w',encoding='utf-8')
# f.write(r.content.decode('UTF-8'))
# f.close()