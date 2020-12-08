# 软件截图
v1.0 的截图：  
![image](https://github.com/jelly-lemon/contrl_sys_ui/blob/UseTableView/img/%E4%B8%BB%E7%95%8C%E9%9D%A2.png)



# 版本更新说明
v1.4.2（2020/7/24）
新功能：   
- 添加打开日志菜单


v1.4.1（2020/7/22）
优化：
- 有问题机器编号


v1.4（2020/7/21）
重大更新：   
- 使用生产者消费者模型，主线程往队列里面放命令，子线程从队列里面读命令。
生产者是主线程，生产命令，子线程是消费者，根据命令执行，然后返回结果给主线程。  


v1.3.2（2020/7/15）   
修复 BUG：
- 表格单元内容过多时显示不全的问题
- 发送控制代码抛出句柄无效的问题

新功能：
- 输出框能够右键菜单清屏
- 增加一键减少、增加防风角度

打包命令：      
pyinstaller MainWindow.spec
可以把依赖文件一起打包至目标文件夹下了。
 

v1.3.1（2020/7/13）   
修复 BUG：
- 修复读取成员数逻辑错误
- 修复第一次打开软件时总是读取不到串口（CPU 要等一下）
   
新功能：
- 能够写入、读取配置

打包命令：
pyinstaller MainWindow.py  --hidden-import=typing --hidden-import=PySide2.QtXml --i=./other/logo.ico --noconsole

v1.3（2020/7/9）   
特点：  
- 加入窗口图标，exe 图标
- 打包后文件最小都有 32 MB
   
打包命令：    
pyinstaller MainWindow.py  --hidden-import=typing --hidden-import=PySide2.QtXml --i=./other/logo.ico --noconsole

v1.2（2020/7/8）   
特点：  
- 加入产品密钥验证

打包命令：   
pyinstaller MainWindow.py -p=C:\Users\Administrator\AppData\Local\Programs\Python\Python36-32\Lib\site-packa
ges\shiboken2 -F  --hidden-import=typing --hidden-import=PySide2.QtXml --i=./other/app.ico --noconsole

# 重要软件包版本
wmi     1.5.1 （获取 CPU 序列号）   
pyDes   2.0.1 （加密解密）    

