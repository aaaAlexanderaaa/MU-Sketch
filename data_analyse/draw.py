import json
import matplotlib.animation as ani
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['STZhongsong']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False


# result_4096_cu=json.loads(open('result_4096_mu','r').read())
# result_1024_cu=json.loads(open('result_mycu','r').read())
result_cu=json.loads(open('result_16384_mu','r').read())
result_mv=json.loads(open('result_16384_mv','r').read())

# result_cu=json.loads(open('result_mycu','r').read())
# result_mv=json.loads(open('result_mymv','r').read())

df0= pd.DataFrame(result_cu)
df0=df0.drop(['s_b_get'],axis=0)
df0.index=df0.index + '_cu'
df1= pd.DataFrame(result_mv)
df1=df1.drop(['s_b_get'],axis=0)
df1.index=df1.index+ '_mv'

dfall=pd.concat([df0,df1],axis=0)
dfall = dfall.transpose()
indexmap=list(range(20000,2240000,20000))
dfall.index=indexmap
def draw(x,dfall,xlabel,ylabel,title,rename):
    df_dst=dfall[x]
    df_dst.columns=rename

    color =  ['red', 'green', 'blue', 'orange','cyan','pink','olive','gray','black']
    fig = plt.figure(figsize=(10, 6.5))
    plt.xticks(rotation=45, ha="right", rotation_mode="anchor") #rotate the x-axis values
    plt.subplots_adjust(bottom = 0.2, top = 0.9) #ensuring the dates (on the x-axis) fit in the screen
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    def buildmebarchart(i=int):
        plt.legend(df_dst.columns)
        p = plt.plot(df_dst[:i].index, df_dst[:i].values) #note it only returns the dataset, up to the point i
        for i in range(len(df_dst.columns)):
            p[i].set_color(color[i]) #set the colour of each curve
    import matplotlib.animation as ani
    animator = ani.FuncAnimation(fig, buildmebarchart, interval = 100)
    plt.show()

def best_fit(X, Y):

    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)
    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2
    b = numer / denum
    a = ybar - b * xbar
    print('best fit line:y = {:.2f} + {:.2f}x'.format(a, b))
    return a, b

def pointdraw(x,dfall,xlabel,ylabel,title,rename):
    df_dst=dfall[x]
    df_dst.columns=rename


    color =  ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    markers=['o','v','^','s','+']
    fig = plt.figure(figsize=(10, 6.5))
    plt.xticks(rotation=45, ha="right",fontsize=16, rotation_mode="anchor") #rotate the x-axis values

    plt.subplots_adjust(bottom = 0.2, top = 0.9) #ensuring the dates (on the x-axis) fit in the screen

    plt.tick_params(labelsize=14)
    # plt.ylabel(ylabel,fontsize=14,fontproperties='Times New Roman')
    # plt.xlabel(xlabel,fontsize=16,fontproperties='Times New Roman')
    # plt.title(title,fontsize=18,fontproperties='Times New Roman')
    plt.ylabel(ylabel, fontsize=14)
    plt.xlabel(xlabel, fontsize=16)
    plt.title(title, fontsize=18)

    #note it only returns the dataset, up to the point i
    for j in range(len(df_dst.columns)):
        plt.scatter(df_dst.index, df_dst[[df_dst.columns[j]]].values,s=16,c=color[j],label=rename[j],marker=markers[j])
        yy=[]
        for yyy in df_dst[[df_dst.columns[j]]].values.tolist():
            yy.append(yyy[0])
        a, b = best_fit(df_dst.index,yy )
        yfit = [a + b * xi for xi in df_dst.index]
        # p=plt.plot(df_dst.index,yfit,linewidth=2,label=rename[j],c=color[j])
        # p[2*j+1].set_color(color[j])
        # p[2 * j ].set_color(color[j])
    # for i in range(len(df_dst.columns)):
    #     p[i].set_color(color[i]) #set the colour of each curve
    import matplotlib.animation as ani
    # animator = ani.FuncAnimation(fig, buildmebarchart, interval = 100)
    plt.legend(fontsize=14)
    plt.show()

def onlydraw(x,dfall,xlabel,ylabel,title,rename):
    df_dst=dfall[x]
    df_dst.columns=rename

    color =  ['red', 'green', 'blue', 'orange','cyan','pink','olive','gray','black']
    plt.figure(figsize=(10, 6.5))
    plt.xticks(rotation=45, ha="right", rotation_mode="anchor") #rotate the x-axis values
    plt.subplots_adjust(bottom = 0.2, top = 0.9) #ensuring the dates (on the x-axis) fit in the screen
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.legend(loc='best')
    p = plt.plot(df_dst.index, df_dst.values) #note it only returns the dataset, up to the point i
    for i in range(len(df_dst.columns)):
        p[i].set_color(color[i]) #set the colour of each curve
    plt.show()

if __name__=='__main__':
    # x=['correct_top1000_cu','correct_top1000_mv']
    # rename=['MU-Sketch Top1000 Precision','MV-Sketch Top1000 Precision']
    # x = ['pjxdwc_byall_cu','pjxdwc_bytop1000_cu']
    # rename=['MU-Sketch平均相对误差（基于全流量）', 'MU-Sketch平均相对误差（基于Top1000）']
    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均相对误差', 'MU-Sketch在不同流量下平均相对误差随数据包数量变化图', rename)
    # x = ['pjxdwc_bytop1000_cu', 'pjxdwc_bytop500_cu', 'pjxdwc_bytop100_cu']
    # rename = [ 'MU-Sketch平均相对误差（基于Top1000）', 'MU-Sketch平均相对误差（基于Top500）',
    #           'MU-Sketch平均相对误差（基于Top100）']
    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均相对误差', 'MU-Sketch在不同流量下平均相对误差随数据包数量变化图', rename)
    # x = ['pjjdwc_byall_cu', 'pjjdwc_bytop1000_cu']
    # rename = ['MU-Sketch平均绝对误差（基于全流量）', 'MU-Sketch平均绝对误差（基于Top1000）']
    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均绝对误差', 'MU-Sketch在不同流量下平均绝对误差随数据包数量变化图', rename)
    # x = [ 'pjjdwc_bytop1000_cu', 'pjjdwc_bytop500_cu', 'pjjdwc_bytop100_cu']
    # rename = [ 'MU-Sketch平均绝对误差（基于Top1000）', 'MU-Sketch平均绝对误差（基于Top500）',
    #           'MU-Sketch平均绝对误差（基于Top100）']
    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均绝对误差', 'MU-Sketch在不同流量下平均绝对误差随数据包数量变化图', rename)
    # x = ['pjxdwc_bytop1000_cu', 'pjxdwc_bytop1000_mv']
    # rename = ['MU-Sketch平均相对误差（基于Top1000）', 'MV-Sketch平均相对误差（基于Top1000）']
    # x = ['pjjdwc_bytop1000_cu', 'pjjdwc_bytop1000_mv']
    # rename = ['MU-Sketch平均绝对误差（基于Top1000）', 'MV-Sketch平均绝对误差（基于Top1000）']
    # x = ['pjxdwc_byall_cu', 'pjxdwc_byall_mv']
    # rename = ['MU-Sketch平均相对误差（基于全流量）', 'MV-Sketch平均相对误差（基于全流量）']
    # x = ['pjjdwc_byall_cu', 'pjjdwc_byall_mv']
    # rename = ['MU-Sketch平均绝对误差（基于全流量）', 'MV-Sketch平均绝对误差（基于全流量）']
    # onlydraw(x, dfall,'交换机测量的数据包数量','Precision',rename)


    x = ['correct_top100_cu','correct_top200_cu','correct_top500_cu','correct_top1000_cu']
    rename=['MU-Sketch Top100准确率','MU-Sketch Top200准确率','MU-Sketch Top500准确率','MU-Sketch Top1000准确率']
    pointdraw(x, dfall,'交换机测量的数据包数量','Precision','MU-Sketch在不同K值下准确率随数据包数量变化图',rename)
    # x = ['correct_top100_cu','correct_top100_mv']
    # rename=['MU-Sketch Top100 Precision','MV-Sketch Top100 Precision']
    # pointdraw(x, dfall, '交换机测量的数据包数量', 'Precision', 'MU-Sketch和MV-Sketch准确率随数据包数量变化图', rename)

    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均绝对误差', 'MU-Sketch和MV-Sketch平均绝对误差（基于全流量）随数据包数量变化图', rename)
    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均相对误差', 'MU-Sketch和MV-Sketch平均相对误差（基于全流量）随数据包数量变化图', rename)
    # pointdraw(x, dfall, '交换机测量的数据包数量', '平均绝对误差', 'MU-Sketch和MV-Sketch平均绝对误差（基于Top1000）随数据包数量变化图', rename)
    # pointdraw(x, dfall,'交换机测量的数据包数量','平均相对误差','MU-Sketch和MV-Sketch平均相对误差（基于Top1000）随数据包数量变化图',rename)
    # pointdraw(x, dfall,'交换机测量的数据包数量','Precision','MU-Sketch和MV-Sketch准确率随数据包数量变化图',rename)
    print(1)
