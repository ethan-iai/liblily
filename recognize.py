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
    
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    ret_kwargs['tempo'] = tempo

    print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    print(beat_frames)
    # print(beat_frames * 512)

    # Convert the frame indices of beat events into timestamps
    
    return ret_kwargs

def freq_recognize(y, sr, N=4, partial=0.85, delta=0.005, hop_length=512, slice=(0, 0.8), verbose=False):
    y = y[slice[0]: int(slice[1] * len(y))]

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

    fouriers = np.fft.fft(filterd_y)
    freqs = np.fft.fftfreq(len(filterd_y), d=(1/sr))

    return freqs[np.argmax(fouriers)]

    
if __name__ == '__main__':
    y, sr = librosa.load('slices/01.wav')

    freq_hz = freq_recognize(y, sr, verbose=True)
    print(librosa.hz_to_note(freq_hz))