## ss-log-tool工具

编译支持win7的版本，需要使用x86 版本的python3.5环境。

如果需要重新编译可通过安装miniconda

然后在命令行中执行下面两个命令来创建环境。 

```
set CONDA_FORCE_32BIT=1
conda create -n py35-32 python=3.5.4
```

创建后需要 conda activate py35-32 切换到python3.5环境。然后正常pip install pyinstaller。

最后执行 生成新的ss-log-debug.exe

```
python build.py 
```

### PS：
Pyinstall打包后的程序不显示终端
```
方法一：pyinstaller -F mycode.py --noconsole
方法二：pyinstaller -F -w mycode.py （-w就是取消窗口）
https://blog.csdn.net/cool99781/article/details/106063260
```
