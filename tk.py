"""
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
from lxml import etree
import os

json1=[]
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
}
imgurl='https://weixin.zijinshe.com/cms/upload/cover/p1685.png'

# -------创建窗体------
root = Tk()
root.title('练习册下载器')
root.geometry('640x530')
root.iconbitmap('./logo.ico')
# -------创建窗体------

# -------创建下拉框Combobox，只读-------
cmb1 = Combobox(root,state='readonly',width=30)
cmb2 = Combobox(root,state='readonly',width=30)
cmb3 = Combobox(root,state='readonly',width=30)
cmb1['value']=('一年级','二年级','三年级','四年级','五年级','六年级','七年级','八年级','九年级')
cmb2['value']=('数学','语文','英语','课本')
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
def printlist(event):
    global imgurl
    # print(lb.curselection())
    v = lb.curselection()
    # 元祖转换为列表
    i= list(v)
    # print(type(v))
    # # 列表转数字
    # print(json1[i[0]])
    # print(json1[i[0]]["cover"])
    imgurl = json1[i[0]]["cover"]
    # print(imgurl)
    # 定义图片可以显示在Label中
    imgreq = requests.get(imgurl, headers=headers)
    image = Image.open(BytesIO(imgreq.content))
    tk_image = ImageTk.PhotoImage(image)
    # 动态更新标签中图片https://www.jb51.net/article/162969.htm
    imglabel.config(image=tk_image)
    imglabel.image=tk_image #keep a reference!
# 绑定双击列表事件
lb.bind('<Double-Button-1>',printlist)
# -------创建列表框Listbox-------

# -------创建Label标签展示练习册封面-------
imglabel=Label(root)
imglabel.grid(row=3,column=2)
# -------创建Label标签展示练习册封面-------

# -------获取教材列表按钮组件-------
# 获取教材列表函数
def huoquliebiao(nianji,kemu,xueqi):
    global json1
    url = "https://weixin.zijinshe.com/cms/upload/site/book-list/wb_lxc_grade_{}_course_{}_volume_{}.json".format(str(nianji),str(kemu),str(xueqi))
    # 课本下载URL：https://weixin.zijinshe.com/cms/upload/site/book-list/wb_kb_grade_5_volume_2.json
    url2 = "https://weixin.zijinshe.com/cms/upload/site/book-list/wb_kb_grade_{}_volume_{}.json".format(str(nianji),str(xueqi))
    # print(type(json1))
    # print(type(json1[0]))
    # print(json1[0])
    # print(url)
    lb.delete(0,END)
    if kemu==4:
        response2 = requests.get(url2, headers=headers)
        json1=response2.json()
        json1 = sorted(json1, key=lambda x: x["version"])
    else:
        response = requests.get(url, headers=headers)
        json1 = response.json()
        json1 = sorted(json1, key=lambda x: x["version"])
    for json in json1:
        # print("版本是：{}。名称是：{}。id是：{}。".format(json['version'],json["name"],json["id"]))
        lb.insert(END,"{}.{}.{}.".format(json['version'],json["name"],json["id"]))
    # print(json1[0].get('name'))

# 列表选取函数
def huoqutushu():
    nianji= cmb1.current()+1
    kemu = cmb2.current()+1
    xueqi = cmb3.current()+1
    # print(cmb1.current()+1)
    # print(cmb3.current()+1)
    huoquliebiao(nianji,kemu,xueqi)
    # print(type(cmb1.current()))
# huoquliebiao(1,1,1)
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
def pachong():
    # 还没有写判断是否为空路径，例子在https://blog.csdn.net/weixin_42183408/article/details/88379191
    path = save_entry.get()
    kid = list(lb.curselection())
    jid=json1[kid[0]]["id"]
    url='http://weixin.zijinshe.com/cms/upload/site/book/{}.html'.format(jid)
    fengmianurl=json1[kid[0]]["cover"]
    # print(url)
    # print(path)
    # print(headers)
    response = requests.get(url, headers=headers)
    html = response.text.encode('iso-8859-1').decode('utf8')
    # print(html)
    html=etree.HTML(html)
    html_data2 = html.xpath('//div[@class="row"]//button/@id')
    url1 = "http://weixin.zijinshe.com/cms/upload/page/"
    for i in range(len(html_data2)):
        # 更新下载进度条和下载数量
        progress["value"]=(i+1)/len(html_data2)*100
        progress.update()
        shuliang["text"]="{}/{}".format(i+1,len(html_data2))
        html_data2[i] = url1 + html_data2[i][2:] + '.jpg'
        # print(html_data2[i])
        r = requests.get(html_data2[i], headers=headers)
        f = open(path+'\\'+str(i+1).zfill(3)+ '.jpg','wb')
        f.write(r.content)
        # print("第%d张图片下载完毕" % (i + 1))
    r = requests.get(fengmianurl,headers=headers)
    f = open(path + '\\' + 'fengmian.jpg', 'wb')
    f.write(r.content)

# 定义检测是否选择教材和正确路径函数
def is_entry_right():
    if  lb.curselection() and os.path.exists(save_entry.get()):
        pachong()
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
