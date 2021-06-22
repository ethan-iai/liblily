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
    
    tempo, beat_samples = librosa.beat.beat_track(y=y, sr=sr, units='samples')
    ret_kwargs['tempo'] = tempo

    print('Estimated tempo: {:.2f} bpm'.format(tempo))
    # print(beat_frames * 512)

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
