# npu_check_electricity

*✨ 西工大电费查询脚本 ✨*

你是否也曾遭遇过宿舍突然停电的悲惨瞬间呢，此项目可以实现绑定宿舍、定时获取宿舍电费、当宿舍电费小于一定值后推送消息提示该充电费啦~

# 如何使用

### 使用编译好的exe

* 打开[Release](https://github.com/qllokirin/npu_check_electricity/releases/latest)下载`bind_room.exe`和`check_electricity.exe`

* 运行`bind_room.exe`按照提示绑定宿舍，绑定完成后会在同级目录下生成一个`check_electricity.json`，内如大致如下所示，`campus`、`building`、`room`请勿随意更改，`warning_electric`为提示阈值，小于`warning_electric`时会弹窗提示

  ```
  {
      "campus": "xxxx",
      "building": "xxxx",
      "room": "xxxx",
      "warning_electric": 10
  }
  ```

  若需重新绑定再次运行`bind_room.exe`即可

* 运行`check_electricity.exe`即可查询电量是否小于阈值，小于阈值时会弹窗，大于阈值时什么都不会发生

  若要检测功能是否正常，可以在`check_electricity.json`中修改`warning_electric`的值为一个很大的值，看看是否会弹窗

  ![dd2b24897f23acc3de0c5e315a221289](https://s2.loli.net/2025/05/17/yKFRP38nS6COVjo.png)

* **如何实现长期持久的检测**

  > 这里使用windows开机自启动的功能实现，若有其他想法也可以

  右键`check_electricity.exe`创建一个快捷方式

  ![image-20250517161018997](https://s2.loli.net/2025/05/17/4kz9dvHutocAQDh.png)

  打开开机自动文件夹，在路径框输入启动然后回车，在这个路径里的文件都会自动开机自动运行

  ![image-20250517161312207](https://s2.loli.net/2025/05/17/LxuPpvkiXKC9UrQ.png)

  然后把刚刚创建的**快捷方式**拖入此文件夹即可，这样的话每次电脑开机即可执行一次检测

  ![image-20250517161507021](https://s2.loli.net/2025/05/17/iOuSdTYXeL93QlU.png)

### 源码运行

绑定宿舍

```
python bind_room.py
```

电费检查

```
python check_electricity.py
```

开机自启动实现方法参照上面

创建一个`check_electricity.bat`写入下面的内容，路径自己替换，然后放入开机自动文件夹即可

```
start "" pythonw.exe {你的路径}\check_electricity.py
```

# 有关推送方式

考虑到并非所有人都有一台一直运行的服务器，所以用开机自启动弹窗提示的方式也算是人人都可以实现了。若有服务器可以考虑使用邮箱推送，或者QQ机器人http请求推送，或者sever酱之类的微信推送。

# 致谢

https://github.com/cheanus/Automation/blob/main/NoticeElectricity.py