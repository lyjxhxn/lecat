import requests
from lxml import etree
import re,os,time
import threadpool
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 屏蔽 证书验证错误代码
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


pool = threadpool.ThreadPool(5)
#http://parse.gitcms.com/mdparse/url.php
class LeCat():
    def __init__(self):
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
        self.host_adders = "http://www.30ts.com"
        self.sohu = "http://sohu.zuida-163sina.com"
        self._path = "E:\\乐猫"
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def get_down(self,vid):
        global title
        global juji
        api_url = "http://gitcms.bceapp.com/post.php"
        data = {"vid":vid}
        html_json = requests.post(api_url,data=data,headers = self.headers).json()
        title = html_json.get("PlayName")
        m3u8_url = html_json.get("PlayModel")
        juji = html_json.get("PlayList")
        return m3u8_url

    def search(self,name):
        seach_url = "http://www.30ts.com/index.php?m=vod-search"
        data = {
            "wd": name,
            "submit":""}
        html = requests.post(seach_url,data=data,headers =self.headers)
        html.encoding = "utf-8"
        html_et = etree.HTML(html.text)
        page_list = html_et.xpath('//ul[@class="stui-vodlist clearfix"]')
      
        n = 1
        for i in page_list:
            player_list = i.xpath('./li/a/@href')
            title_list = i.xpath('./li/a/@title')
      
        for title0 in title_list:
            print('{:>2}：{}'.format(n,title0))
            # print(str(n)+": "+title0)
            n += 1
        
        while True:
            try:
                xuhao = int(input("请输入想要下载的序号："))
                if 1 <= xuhao <= len(title_list):
                    player_url = player_list[xuhao-1]
                    break
            except:
                print("输入有误，请重新输入！")


        return player_url
        
    def show_url(self,play_url):
        html = requests.get(self.host_adders+play_url,headers = self.headers)
        html.encoding = "utf-8"
        html_et = etree.HTML(html.text)
        ul_list = html_et.xpath('//ul[@class="stui-content__playlist clearfix"]')
        
        for i in ul_list:
            play_hrefs = i.xpath('./li/a/@href')
            play_pages = i.xpath('./li/a/text()')
        n = 1
        play_hrefs.reverse() #逆序列表
        play_pages.reverse() #逆序列表
        for show_juji in play_pages:
            print('{:>2}：{}'.format(n,show_juji))
            # print(str(n)+": "+show_juji)
            n += 1

        while True:
            try:
                xuhao = int(input("请选择下载的内容的序号："))
                if 1 <= xuhao <= len(play_pages):
                    play_href = play_hrefs[xuhao-1]
                    break
            except:
                print("输入有误，请重新输入")
        # print(play_href)
        return play_href
        


    def get_vid(self,play_href):
        html = requests.get(self.host_adders+play_href,headers = self.headers).text
        vid1 = re.search(r"%24(\d{8})-1-1-1-1-1-",html).group(1)
        vid2 = play_href.split("-")[-1].split(".")[0]
        vid = "%s-1-%s-1-1-1-1"%(vid1,vid2)
        return vid

    def down_MP4(self,down_url):
        path = "E:\\乐猫\\%s-%s.mp4"%(title,juji)
        start = time.time()
        size = 0
        resopnse = requests.get(down_url,headers = self.headers,stream = True)
        chunk_size = 1024
        content_size = int(resopnse.headers["content-length"])
        
        if resopnse.status_code == 200:
            print("[文件大小]：%0.2f MB,默认下载路径E:\\乐猫"%(content_size / chunk_size / 1024))
            with open(path,"wb") as file:
                for i in resopnse.iter_content(chunk_size=chunk_size):
                    file.write(i)
                    file.flush()
                    size += len(i)
                    aaa = (size/content_size)*50
                    # print("\r"+"[当前进度]:%s%.2f%%"%(">"*int(size*20/ content_size),float(size / content_size *100)),end = "")
                    print('\r[当前进度]:{:50}>{:0.2f} %'.format('>'*int(aaa), aaa*2),end = "")
            end = time.time()
            print("\n"+"《%s-%s》下载完成!用时%.2f秒。\n"%(title,juji,end-start))
        else:
            print("下载失败，请稍后再试！")
        

    def parsing(self,m3u8_url):
        if "m3u8" in m3u8_url:
            html = requests.get(m3u8_url,headers =self.headers,verify=False).text
            m3u8_html = html.split('\n')
            if len(m3u8_html) > 4:
                jx_m3u8 = m3u8_url
            else:
                tiaozhuan_link = m3u8_html[2]
                if "sohu" in m3u8_url:
                    jx_m3u8 = self.sohu + tiaozhuan_link
                elif "youku" or "iqiyi" in m3u8_url:
                    you_iq = m3u8_url.replace(m3u8_url.split('/')[-1],'')
                    jx_m3u8 = you_iq + tiaozhuan_link
                else:
                    print("此链接暂不支持下载：%s")%m3u8_url
            print(jx_m3u8)
            return jx_m3u8
        else:
           self.down_MP4(m3u8_url)
           self.main()

    def downloads(self,m3u8_url):
        global ts_qianzhui
        html = requests.get(m3u8_url,headers = self.headers,verify=False)
        data = []
        if html:
            html = html.text.split('\n')
            if "sohu" not in m3u8_url:
                ts_qianzhui = m3u8_url.replace(m3u8_url.split('/')[-1],'')
            else:
                ts_qianzhui = self.sohu
            for name in html:
                if '.ts' in name:
                    url = ts_qianzhui + name
                    data.append(url)
        self.file_size = len(data)
        return data

    def down_ts(self,datas):
        if datas:
            self.jindu += 1 
            resopnse = requests.get(datas,headers = self.headers,verify=False,stream = True)
            if resopnse.status_code == 200:
                for i in resopnse.iter_content(chunk_size=1024):
                    with open('E:/乐猫/temp/%s/%s/%s'%(title,juji,datas.split('/')[-1]),'ab') as f: #ts完整路径进行切片，取最后一个值
                        f.write(i)
                        f.flush()
                aaa = (self.jindu / self.file_size) * 50
                s = '\r[当前进度]:{:50}>{:0.2f} %'.format('>'*int(aaa), aaa*2)
                print(s,end='')
            else:
                print("%s文件丢失"%datas)
        else:
            print("没有找到ts文件，不支持下载")
            

    def allok(self,ts_names):
        print()
        print("正在校检文件完整性...")
        for ts_name in ts_names:
            ts_path = "E:\\乐猫\\temp\\%s\\%s\\%s"%(title,juji,ts_name)
            with open("E:\\乐猫\\%s-%s.ts"%(title,juji),"ab+") as f:
                if os.path.exists(ts_path):
                    pass
                else:
                    print("%s文件丢失,尝试再次下载"%ts_name)
                    move = requests.get(ts_qianzhui + ts_name,headers = self.headers,verify=False).content
                    with open(ts_path,'wb') as ls: 
                        ls.write(move)
                        ls.close()
                nb = open(ts_path,"rb")
                f.write(nb.read())
                nb.close()
                f.close()
                # print("正在写入%s"%ts_name)
        os.system('rmdir /s/q E:\\乐猫\\temp')     
        
       
        
       
        
    def run(self,name):
        self.jindu = 0
        self.file_size = 0
        play_url = self.search(name)
        play_href = self.show_url(play_url)
        vid = self.get_vid(play_href)
        m3u8_url = self.get_down(vid)
        jx_m3u8 = self.parsing(m3u8_url)
        datas = self.downloads(jx_m3u8)
        print('正在缓存%s-%s...'%(title,juji))
        start = time.time()
        path = 'E:/乐猫/temp/%s/%s'%(title,juji)
        if not os.path.exists(path):
            os.makedirs(path)
        requests = threadpool.makeRequests(self.down_ts,datas) #进程传入任务及完成ts链接
        [pool.putRequest(req) for req in requests] #启用限制进程数
        pool.wait() #等待
        ts_names = []
        for i in datas:
            ts = i.split("/")[-1]
            ts_names.append(ts)
        self.allok(ts_names)
        end = time.time()
        print("《%s-%s》下载完成!用时%.2f秒,默认下载路径E://乐猫"%(title,juji,end-start))
        
       
       
    def main(self):
        __version__ = '1.3'
        NAME = '乐猫TV资源下载'   
        msg = """
                +------------------------------------------------------------+
                |                                                            |
                |              欢迎使用{} V_{}                  |
                |                                                            |
                |                             Copyright (c) 2019   lyjxhxn   |
                +------------------------------------------------------------+
                """.format(NAME, __version__)
        print(msg)
        name = input("请输入想要下载的视频:")
        self.run(name)




if __name__ == "__main__":
    lecat = LeCat()
    while True:
        lecat.main()