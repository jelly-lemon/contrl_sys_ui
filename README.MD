# 软件截图
![image](https://github.com/jelly-lemon/contrl_sys_ui/blob/UseTableView/img/%E4%B8%BB%E7%95%8C%E9%9D%A2.png)

# 更新说明
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

