import numpy as np
from numpy.core.fromnumeric import shape
import numpy.fft as nf
import scipy.io.wavfile as wf
import librosa

# 读取文件，采样率
music_path = './long_demo.wav'
# sigs, sr = librosa.load(music_path)
sample_rate, sigs = wf.read(music_path)

# 处理双声道
if len(sigs.shape) > 1:
    sigs = np.sum(sigs, axis=1)/2
    sigs = sigs / (2**15)


# 时间序列
times = np.arange(sigs.size) / sample_rate

# 对原始信号进行FFT
freqs = nf.fftfreq(sigs.size, times[1]-[0])
complex_array = nf.fft(sigs)
pows = np.abs(complex_array)

# 以1024个采样点为一个window
lastPieceArray = nf.fft(sigs[:1024])
lastTimeArray = times[:1024]
lastSpectrum = np.abs(lastPieceArray)
fluxArray =[]

# 逐个窗口进行差分，提取频谱通量
for i in range(1024, sigs.size-1024, 1024):
    windowArray = nf.fft(sigs[i:i+1024])
    spectrum = np.abs(windowArray)
    flux = 0.0
    for j in range(1024):
        a = spectrum[j]
        b = lastSpectrum[j]
        value = a - b
        if value < 0.0:
            value = 0
        flux += value
    fluxArray.append(flux)
    lastSpectrum = spectrum

# 以每个窗口前后十个窗口进行平均设置阈值
threshold_size = 20   # 窗口值的选取？0.5s一拍
thresholdArray = []
for i in range(0, len(fluxArray)):
    start = max(0, i - threshold_size)
    end = min(len(fluxArray)-1, i+threshold_size)
    mean = 0.0
    for j in range(start, end):
        mean += fluxArray[j]
    mean /= (end-start)
    thresholdArray.append(mean*2.1)

# 筛选节拍点
peakArray = []
for i in range(0, len(thresholdArray)):
    if(thresholdArray[i] <= fluxArray[i]):
        peakArray.append(fluxArray[i])
    else:
        peakArray.append(float(0))

count = 0
peaks = []
peakNumber = []
peakValue = []
shold = []
for i in range(1, len(thresholdArray)-1):
    if((peakArray[i] > peakArray[i+1]) and (peakArray[i] > peakArray[i-1])):
        peaks.append(peakArray[i])
        count += 1
        peakNumber.append(i)
        peakValue.append(peakArray[i])
        shold.append(thresholdArray[i])
    else:
        peaks.append(float(0))

# 调用librosa库
y, sr = librosa.load(music_path, sr=sample_rate)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

# 去除过近的
cnt = 0
for i in range(len(peakValue)):
    if(i == 0):
        j=0
    else:
        j=i-1
    if((peakNumber[i]-peakNumber[j])<=4):
        cnt += 1

average = np.sum(peakValue) / len(peakValue)
maxPeak = max(peakValue)

# 输出识别出的count和librosa提取的节拍对比
count = float(count)

long = sigs.size / sample_rate
print("************       final       *************")
print("************       final       *************")
print("my onset detection is          " + str((count * 60 / long)))
print("librosa's onset detection is   " + str(tempo))
print("************       final       *************")
print("************       final       *************")

