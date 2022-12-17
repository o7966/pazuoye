"""
    2022-12-16
    跟随资源站点修改代码逻辑。
    2020-4-21
    给孩子下载联系册答案。0.2整理了代码结构。
"""
from tkinter import *
import tkinter.messagebox
from tkinter.filedialog import askdirectory
from tkinter.ttk import *
from PIL import Image,ImageTk
from io import BytesIO
import requests
import os
import time
from json import JSONDecoder,JSONDecodeError
import re
import base64


headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.9(0x17000929) NetType/WIFI Language/zh_CN",
    # "Referer": "https://weixin.zijinshe.com/cms/webapp/home/answer/index.html",
    "Origin": "https://weixin.zijinshe.com"
}
# 一个全局变量用来接受教材封面
imgurl=''

# 解析课程列表Json函数
NOT_WHITESPACE=re.compile(r'[^\s]')
def decode_stacked(document,pos=0,decoder=JSONDecoder()):
    while True:
        match = NOT_WHITESPACE.search(document,pos)
        if not match:
            return
        pos=match.start()

        try:
            obj,pos = decoder.raw_decode(document,pos)
        except JSONDecodeError:
            raise
        yield  obj

# 年级、科目、上下册，返回base64后查询语句。
def get_select(grades,course,volume):
    select1="""SELECT * FROM ossobject [*] o WHERE o.book.gradesStr like  '%{},%' \
AND o.book.course in ('{}') AND o.book.volume in  ('{}','3') \
AND o.book.category in  ('keben','jiaofu','keben_answer','jiaofu_answer')""".format(grades,course,volume)
    select1_base64=base64.b64encode(select1.encode())
    return select1_base64

# -------创建窗体------
root = Tk()
root.title('练习册下载器')
root.geometry('640x530')
# root.iconbitmap('./logo.ico')
# -------创建窗体------

# -------创建下拉框Combobox，只读-------
cmb1 = Combobox(root,state='readonly',width=30)
cmb2 = Combobox(root,state='readonly',width=30)
cmb3 = Combobox(root,state='readonly',width=30)
cmb1['value']=('一年级','二年级','三年级','四年级','五年级','六年级','七年级','八年级','九年级')
cmb2['value']=('数学','语文','英语','物理','化学','生物','历史','道德与法制')
cmb3['value']=('上半学期','下半学期')
# Combobox默认选项
cmb1.current(0)
cmb2.current(0)
cmb3.current(0)
cmb1.grid(row=0,column=0,pady=5)
cmb2.grid(row=1,column=0,pady=5)
cmb3.grid(row=2,column=0,pady=5)
# -------创建下拉框Combobox-------

# -------创建列表框Listbox-------
# 创建滚动条
y_scroll = Scrollbar(root)
y_scroll.grid(row=3,column=1,sticky=N+S)
x_scroll = Scrollbar(root,orient=HORIZONTAL)
x_scroll.grid(row=4,column=0,sticky=W+E)
# 创建列表框绑定滚动条
lb = Listbox(root,height=15,width=40,yscrollcommand=y_scroll.set,xscrollcommand=x_scroll.set)
lb.grid(row=3,column=0,padx=15,pady=5)
# 更新滚动条
y_scroll.config(command=lb.yview)
x_scroll.config(command=lb.xview)

# 创建列表框双击显示图片函数
def printlist():
    url="https://prd.oss.leziedu.com/"
    global imgurl
    # print(lb.curselection())
    v = lb.curselection()
    # 元祖转换为列表
    i= list(v)
    # list1[i[0]] 列表转换成字符
    imgurl = "{}{}".format(url,list1[i[0]]["thumbCoverPath"])
    # print(imgurl)
    # 定义图片可以显示在Label中
    imgreq = requests.get(imgurl, headers=headers)
    image = Image.open(BytesIO(imgreq.content))
    tk_image = ImageTk.PhotoImage(image)
    # 动态更新标签中图片https://www.jb51.net/article/162969.htm
    imglabel.config(image=tk_image)
    imglabel.image=tk_image #keep a reference!


# 判断列表框是否为空
def is_listbox_right(event):
    if lb.curselection() and lb.get(0):
        printlist()
    else:
        tkinter.messagebox.showwarning('wrong!', '没有找到教材,重新选择！')


# 绑定双击列表事件
lb.bind('<Double-Button-1>', is_listbox_right)



# -------创建列表框Listbox-------

# -------创建Label标签展示练习册封面-------
imglabel=Label(root)
imglabel.grid(row=3,column=2)
# -------创建Label标签展示练习册封面-------

# -------获取教材列表按钮组件-------
# 获取教材列表函数

def huoquliebiao(nianji,kemu,xueqi):
    global list1
    list1=[]
    select1=get_select(nianji,kemu,xueqi).decode("utf-8")
    url="https://zijinshe-common-object.oss-cn-shenzhen.aliyuncs.com/basicbook/wx43cddada7b553cec/bookListInfo_toolBook.json?x-oss-process=json%2Fselect"
    body_data="""<SelectRequest><Expression>{}</Expression>
      <OutputSerialization>
      <JSON>
          </JSON>
          <OutputRawData>true</OutputRawData></OutputSerialization>
    </SelectRequest>""".format(select1)
    # print(body_data)
    req1=requests.post(url=url,data=body_data,headers=headers)
    # print(req1.text)
    lb.delete(0, END)
    req1json=decode_stacked(req1.text)
    for obj in req1json:
        list1.append(obj["book"])
        lb.insert(END, "{}.{}.".format(obj["book"]["fullName"], obj["book"]["id"]))


# 列表选取函数
def huoqutushu():
    # kemu={'数学':1,'语文':2,'英语':3,'物理':5,'化学':6,'生物':7,历史':9,'道德与法制':14}
    kemu_jihe=[1,2,3,5,6,7,9,14]
    nianji= cmb1.current()+1
    kemu = kemu_jihe[cmb2.current()]
    xueqi = cmb3.current()+1
    huoquliebiao(nianji,kemu,xueqi)
    # print(type(cmb1.current()))
but1 = Button(root,text='获取教材列表',command=huoqutushu)


but1.grid(row=5,column=0)
# -------获取教材列表按钮组件-------

# -------定义文件夹选择-------
# 存储地址变量
path = StringVar()
# 选择文件夹的函数
def selectPath():
    path_ = askdirectory()
    path.set(path_)

# 保存地址
save_add = Label(root, text='保存到:')
save_add.grid(row=7,column=0)
# 输入地址
save_entry = Entry(root, width=40, textvariable=path)
save_entry.grid(row=8,column=0)
# 选择地址按钮
path_choose = Button(root, text='选择文件夹', command=selectPath)
path_choose.grid(row=8,column=1)
# -------定义文件夹选择-------

# -------定义下载按钮-------
# 定义实际下载和保存位置函数
def get_target_value(key,dic,tmp_list):
    """
    :param key: 目标key值
    :param dic: Json数据
    :param tmp_list: 储存获取的数据
    :return: list
    """
    if not isinstance(tmp_list,list):
        err="tmp_list: 参数类型错误！"
        return err
    if isinstance(dic,(list,tuple)):
        for v in dic:
            get_target_value(key,v,tmp_list)
    elif isinstance(dic,dict):
        if key in dic.keys():
            tmp_list.append(dic[key])
        for value in dic.values():
            get_target_value(key,value,tmp_list)
    return tmp_list


def pachong():
    res=[]
    v = lb.curselection()
    i= list(v)
    # print(len(list1))
    jsonurl = "https://prd.oss.leziedu.com/basicbook/wx43cddada7b553cec/{}_bookInfo.json".format(list1[i[0]]["id"])
    baseurl = "https://prd.oss.leziedu.com/"
    # print(jsonurl)
    # 解析成字典
    req=requests.get(url=jsonurl,headers=headers)
    # print(type(req.json()))
    dict1=req.json()
    # print(dict1)
    get_target_value("answerPicPath", dict1, res)
    # print(res)
    for i in range(len(res)):
#         # 更新下载进度条和下载数量
        progress["value"] = (i+1)/len(res)*100
        progress.update()
        shuliang["text"] = "{}/{}".format(i+1,len(res))
        res[i] = "{}{}".format(baseurl,res[i])
        # print(res[i])
        r = requests.get(res[i], headers=headers)
        # print(type(i))
        # print(path.get())
        f = open("{}/{}.jpg".format(path.get(),str(i+1).zfill(3)),'wb')
        f.write(r.content)
        # print("第%d张图片下载完毕" % (i + 1))
    r = requests.get(imgurl,headers=headers)
    f = open("{}/fengmian.jpg".format(path.get()), 'wb')
    f.write(r.content)


# 定义检测是否选择教材和正确路径函数
def is_entry_right():
    if lb.curselection() and os.path.exists(save_entry.get()):
        start = time.time()
        pachong()
        stop = time.time()
        print(stop-start)
    else:
        tkinter.messagebox.showwarning('wrong!', '请选择教材和路径！')

# 定义开始下载按钮
download=Button(root,text='下载',command=is_entry_right)
download.grid(row=9,column=1)
# -------定义下载按钮-------

# -------定义下载进度条-------
# 进度条http://www.voidcn.com/article/p-uohzmvuy-bug.html
# https://blog.csdn.net/Speechless_/article/details/84941810
progress=Progressbar(root,maximum=100,orient=HORIZONTAL,length=285,mode='determinate')
progress.grid(row=9,column=0)
# 定义下载进度和数量
shuliang=Label(root)
shuliang.grid(row=9,column=0)
# -------定义下载进度条-------

# 由于tkinter(提示功能)中没有ToolTip功能，所以自定义这个功能如下
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        label = Label(tw, text=self.text, justify=LEFT,
                         background="#ffffe0", relief=SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# ===================================================================
def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

# -------分隔符-------
s = Separator(root,orient = HORIZONTAL)
s.grid(row=6,column=0,sticky = W+E)
# -------分隔符-------

# Add Tooltip
createToolTip(cmb1, '选择年级.')
createToolTip(cmb2, '选择科目.')
createToolTip(cmb3, '选择学期.')

# 主循环
root.mainloop()
