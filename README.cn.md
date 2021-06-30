# Liblily 

## 简介

TODO:

## 加噪与去噪

TODO:

## 节拍识别

TODO:

## 音高识别
### 常见算法
- 并行处理法

    音乐信号在经过预处理后由峰值处理器找出峰点和谷点，产生6个脉序列，由6个并行的基音周期估计器估计基音周期。最后对这些基音估计器的输出作逻辑组合，得出估计值。

    缺点：**误差较大**，甚至会大于100 音分。

- 谐波峰值法

    基于快速傅里叶变换的分析法，将信号通过FFT 变换得到离散的频率谱， 最大峰值对应于基音频率。
    
    缺点：如果乐器谐波比较丰富，很有可能把**二次甚至三次谐波误定为音高**。

- 小波分析法

    小波具有良好的时频特性，能很好地调节时域和频域的分辨率。做基音检测时，小波变换相当于一个中心频率和带宽可调的滤波器，每经一次变换，高频谐波部分就被滤去一半，而基音部分被保存下来，变换后的波形也越来越“ 纯”，最终可确定基音。

    缺点：小波分解的运算量很大，尤其当需要较大的分解尺度时。


### 简介
先用**时域处理法**对音乐信号进行**基音频率**估计， 然后以得到的基音频率为参数设计**数字低通滤波器**。音乐信号经滤波器滤波后，滤除了高频分量，相当于减小了音乐信号的频宽， 排除了谐波成分的干扰。在此基础上再做**FFT** 就可得到准确的音高。

![process](https://github.com/ethan-iai/liblily/blob/master/images/process.png)

## 下载与安装
```shell
git clone https://github.com/ethan-iai/liblily.git
cd liblily
pip install -r requirements.txt
pip install -e .
```

## 使用
对`demo.wav`添加**高斯噪声**，并去除添加的噪声，将结果保存到指定目录。同时，输出对`demo.wav`的节拍(bpm)与音高的检测结果。通常，去噪后的声音样本会被保存到`~/.liblily`，可以通过修改`LIBLILY_SRC_DIR`环境变量改变保存结果的目录。

```shell
python -m liblily.cli demo.wav --method guass 
```

更进一步，你可以通过命令行设定算法的**参数**。

```shell
python -m liblily.cli demo.wav --method guass --partial 0.8
```

### 高级
调节算法参数时，可以添加`--verbose`选项，使程序绘制特定图像从而可视化参数的调节情况。

```shell
python -m liblily.cli demo.wav --method guass --partial 0.8 --verbose
```
