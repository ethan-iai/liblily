# Liblily 

## 简介

TODO:

## 加噪与去噪

TODO:

## 节拍识别

TODO:

## 音高识别

TODO:

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
