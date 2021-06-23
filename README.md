# Liblily

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ethan-iai/liblily/tree/master/README.md)
[![cn](https://img.shields.io/badge/语言-cn-yellow.svg)](https://github.com/ethan-iai/liblily/tree/master/README.cn.md)

## Features
- add noises and filter 
- tempo recogintion
- note recogintion
- basic command line tool

## Installation
```shell
git clone https://github.com/ethan-iai/liblily.git
cd liblily
pip install -e .
```

## Examples
add __Guass__ noise to `demo.wav` , filter addtional noises with certain methods and print out the tempo and notes detected. By default, liblily would save results under the `~/.liblily` directory. You could override it by setting the `LIBLILY_SRC_DIR` environment variable to an alternative location.

```shell
python -m liblily.cli demo.wav --method guass 
```

Further more, you can customize the paremeters of algorithm in the command line.

```shell
python -m liblily.cli demo.wav --method guass --partial 0.8
```
### advanced

while tuning the parameters, add `--verbose` in your command to draw "useful" figures with `matplotlib` that visualize the effects of parameters. 

```shell
python -m liblily.cli demo.wav --method guass --partial 0.8 --verbose
```
