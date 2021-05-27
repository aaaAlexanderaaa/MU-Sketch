# MU-Sketch
**本项目为论文《基于软件交换机的网络heavy hitters检测算法设计与实现》的部分相关代码**

其中提供了:

- 本文算法MU-Sketch的[P4代码实现](https://github.com/aaaAlexanderaaa/MU-Sketch/tree/main/mu-Sketch)

- 参考算法[MV-Sketch](https://github.com/Grace-TL/MV-Sketch)的[P4代码实现](https://github.com/aaaAlexanderaaa/MU-Sketch/tree/main/mv-Sketch)

- 实验使用的[数据集](https://github.com/aaaAlexanderaaa/MU-Sketch/tree/main/datas)

此外还提供了:

- 当前网络中heavy hitter的实时展示的web实现代码，在[flask_show](https://github.com/aaaAlexanderaaa/MU-Sketch/tree/main/flask_show)中

- 向指定网卡快速发包同时统计流信息的工具，在[senddata.py](https://github.com/aaaAlexanderaaa/MU-Sketch/blob/main/senddata.py)中

- 批量读取bmv2交换机寄存器的工具，在[runtime_Register.py](https://github.com/aaaAlexanderaaa/MU-Sketch/blob/main/runtime_Register.py)中

- 部分bmv2交换机hash函数的python实现,包括identity,crc32,crc16,cksum16，在[/data_analyse/hash.py](https://github.com/aaaAlexanderaaa/MU-Sketch/blob/main/data_analyse/hash.py)中

- 实验相关数据分析使用的代码，在[/data_analyse/dat_ana.py](https://github.com/aaaAlexanderaaa/MU-Sketch/blob/main/data_analyse/dat_ana.py)中

- 数据分析结果绘图使用的代码，在[/data_analyse/draw.py](https://github.com/aaaAlexanderaaa/MU-Sketch/blob/main/data_analyse/draw.py)中
