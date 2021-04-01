import matplotlib.pyplot as plt
import numpy as np

x1 = np.arange(200, 1200, 200)  # x轴数据
y11 = [0.706, 0.777, 0.825, 0.845, 0.862]
y12 = [0.743, 0.806, 0.843, 0.860, 0.873]
y13 = [0.672, 0.759, 0.819, 0.847, 0.864]

x2 = [200, 400, 550]
y21 = [0.752, 0.840, 0.874]
y22 = [0.792, 0.862, 0.887]
y23 = [0.738, 0.838, 0.879]

x3 = np.arange(200, 1200, 200)  # x轴数据
y31 = [0.799, 0.826, 0.855, 0.871, 0.900]
y32 = [0.839, 0.864, 0.869, 0.885, 0.913]
y33 = [0.752, 0.80, 0.839, 0.847, 0.864]
plt.figure(figsize=(5, 3.5))
# 关键句,前两个参数是X、Y轴数据,其他参数指定曲线属性，如标签label，颜色color,线宽linewidth或lw,点标记marker
plt.plot(x1, y11, 'gray', marker='^', label='Twitter15 PPA', linewidth=1, markersize=3)
plt.plot(x1, y12, 'red', marker='^', label='Twitter15 PPA-WAE', linewidth=1, markersize=3)
plt.plot(x1, y13, 'green', marker='^', label='Twitter15 Bi-GCN', linewidth=1, markersize=3)
plt.plot(x2, y21, 'gray', marker='o', label='Twitter16 PPA', linewidth=1, markersize=3)
plt.plot(x2, y22, 'red', marker='o', label='Twitter16 PPA-WAE', linewidth=1, markersize=3)
plt.plot(x2, y23, 'green', marker='o', label='Twitter16 Bi-GCN', linewidth=1, markersize=3)
plt.plot(x3, y31, 'gray', marker='s', label='Weibo PPA', linewidth=1, markersize=3)
plt.plot(x3, y32, 'red', marker='s', label='Weibo PPA-WAE', linewidth=1, markersize=3)
plt.plot(x3, y33, 'green', marker='s', label='Weibo Bi-GCN', linewidth=1, markersize=3)
# 显示图例，前提是plot参数里写上label;loc是图例的位置
plt.legend(loc='best')

# plt.xticks(x)
plt.xlabel('Training samples')
plt.ylabel('Acc.')
plt.ylim(0.65, 0.95)
# plt.title('SNLI测试集随重要性阈值的变化曲线')
plt.savefig('small_sample.png',
            bbox_inches='tight',
            dpi=1200)  # 除了png，还有一些格式如svg，dpi是dot per inch每英寸的像素点数，缺省值80，论文写作一般要求1200或者矢量图
plt.show()  # show函数显示图表会中断程序，直到关闭图像。不要把show写在savefig前，否则保存图像一片空白。最好是注释掉savefig或者show其中一行。
