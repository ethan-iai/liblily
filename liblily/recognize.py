import numpy as np
import librosa
import librosa.display
import scipy.signal

from matplotlib import pyplot as plt

def audio_recognize(y, sr, verbose=False):
    ret_kwargs = dict()
    
    if verbose:
        plt.figure(figsize=(14,5))
        librosa.display.waveplot(y, sr=sr)
        plt.savefig('./wave_figure.jpg')
    
    # call librosa to get note slice 
    # NOTE: we haven't use it to recognize tempo 
    tempo_ref, beat_samples = librosa.beat.beat_track(y=y, sr=sr, units='samples')
    tempo = tempo_recogize(y, sr)
    ret_kwargs['tempo'] = tempo

    print('Estimated tempo: {:.2f} bpm'.format(tempo))
    
    if verbose:
        print('Estimated tempo by librosa: {:.2f} bpm'.format(tempo_ref))
    
    # Convert the frame indices of beat events into timestamps
    beat_cnt = len(beat_samples)
    beat_times = librosa.samples_to_time(beat_samples, sr=sr)
    beat_times = beat_times
    start = beat_samples[0]
    for i, end in enumerate(beat_samples[1 : beat_cnt - 1]):
        freq_hz = freq_recognize(y[start : end], sr, verbose)
        print("period: [{:.2f}, {:.2f}]\tfreq: {:.2f}Hz\tnote: {}".format(beat_times[i], beat_times[i + 1], 
                                                                          freq_hz, librosa.hz_to_note(freq_hz))) 
        start = end

    return ret_kwargs

def tempo_recogize(y, sr):
    # y = y * 32767
    
    # 时间序列
    times = np.arange(y.size) / sr

    # 对原始信号进行FFT
    freqs = np.fft.fftfreq(y.size, times[1]-[0])
    complex_array = np.fft.fft(y)
    pows = np.abs(complex_array)

    # 以1024个采样点为一个window
    lastPieceArray = np.fft.fft(y[:1024])
    lastTimeArray = times[:1024]
    lastSpectrum = np.abs(lastPieceArray)
    fluxArray =[]

    # 逐个窗口进行差分，提取频谱通量
    for i in range(1024, y.size-1024, 1024):
        windowArray = np.fft.fft(y[i:i+1024])
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

    # 去除过近的
    cnt = 0
    for i in range(len(peakValue)):
        if(i == 0):
            j=0
        else:
            j=i-1
        if((peakNumber[i]-peakNumber[j])<=4):
            cnt += 1

    # average = np.sum(peakValue) / len(peakValue)
    # maxPeak = max(peakValue)

    # 输出识别出的count和librosa提取的节拍对比
    count = float(count)

    long = y.size / sr

    # TODO: magic number: 1.6
    # * 1.6 is used to solve the differnce between 
    # scipy.io.wavfile.read() and librosa.load()
    return (count * 60 * 1.62 / long)

def freq_recognize(y, sr, N=4, partial=0.85, delta=0.005, hop_length=512, slice=(0, 0.8), verbose=False):
    y = y[slice[0]: int(slice[1] * len(y))]

    # verbose = True
    if verbose:
        times = librosa.times_like(y, sr, hop_length)
        librosa.display.waveplot(y, sr=sr)    
        plt.savefig('step0.jpg')
        plt.close()
    # verbose = False

    peaks = librosa.util.peak_pick(y, hop_length * 0.4, hop_length * 0.4, 
                                   hop_length * 0.4, hop_length * 0.4, 
                                   delta, hop_length)
    thres = partial * np.mean(y[peaks]) 
    
    if verbose:
        times = librosa.times_like(y, sr, hop_length)
        librosa.display.waveplot(y, sr=sr)    
        plt.vlines(librosa.samples_to_time(peaks), ymin=y.min(), ymax=y.max(), colors='r')
        plt.hlines([thres], xmin=0, xmax=times.max(), colors='y')
        plt.savefig('step1.jpg')
        plt.close()
        # plt.show()
    
    clipped_y = np.zeros_like(y)
    
    for i, num in enumerate(y):
        if num > thres:
            clipped_y[i] = 1
        elif num < -thres:
            clipped_y[i] = -1

    r = librosa.autocorrelate(clipped_y)

    offset = hop_length // 2
    peaks = librosa.util.peak_pick(r[offset: ], hop_length * 0.3, hop_length * 0.3, 
                                   hop_length * 0.3, hop_length * 0.3, 
                                   delta, hop_length)
    peaks = peaks + offset
    est_freq = sr / peaks[np.argmax(r[peaks])]
    # print(est_freq)

    if verbose:
        plt.plot(r)
        plt.vlines(peaks, ymin=r.min(), ymax=r.max(), colors='b')
        plt.savefig('step2.jpg')
        plt.close()

    b, a = scipy.signal.butter(N, est_freq / (0.5 * sr), btype='lowpass', analog=False)
    filterd_y = scipy.signal.lfilter(b, a, y)

    if verbose:
        plt.subplot(3, 1, 1)
        w, h = scipy.signal.freqs(b, a)            # 根据系数计算滤波器的频率响应，w是角频率，h是频率响应
        plt.plot(0.5*sr*w/np.pi, np.abs(h), 'b')
        plt.axvline(est_freq, color='k')
        plt.xlim(0, 0.5 * sr)
        plt.title("Lowpass Filter Frequency Response")
        plt.xlabel('Frequency [Hz]')

        
        plt.subplot(3, 1, 2)
        plt.specgram(y, Fs=sr, scale_by_freq=True, sides='default')
        plt.xlabel('Time [sec]')

        plt.subplot(3, 1, 3)
        plt.specgram(filterd_y, Fs=sr, scale_by_freq=True, sides='default')
        plt.xlabel('Time [sec]')

        plt.savefig('step3.jpg')
        plt.close()

    n = len(filterd_y)
    fouriers = np.abs(np.fft.fft(filterd_y))[ : n // 2]
    freqs = np.fft.fftfreq(n, d=(1/sr))[ : n // 2]
    
    if verbose:
        plt.subplot(1, 2, 1)
        prefs = np.abs(np.fft.fft(y))[ : n // 2]
        plt.xlim(0, 1024)
        plt.vlines(freqs[np.argmax(prefs)], ymin=0, ymax=prefs.max() * 1.2 , colors='r')
        plt.plot(freqs, prefs)
        plt.title("Unfiltered")
        plt.xlabel('Frequency [Hz]')

        plt.subplot(1, 2, 2)
        plt.xlim(0, 256)
        plt.plot(freqs, fouriers)
        plt.vlines(freqs[np.argmax(fouriers)], ymin=0, ymax=fouriers.max() * 1.2, colors='r')
        plt.title("Filtered")
        plt.xlabel('Frequency [Hz]')

        plt.savefig('step4.jpg')
        plt.close()
    
    return freqs[np.argmax(fouriers)]

    
if __name__ == '__main__':
    y, sr = librosa.load('demo.wav')

    freq_hz = audio_recognize(y, sr, verbose=False)
    # print("freq: {:.2f}Hz\tnote: {}".format(freq_hz, librosa.hz_to_note(freq_hz)))
