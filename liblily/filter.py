import numpy as np
import numpy.fft as nf
import scipy.signal as ss

# def filter_1():
#     for i in fft_pows:
#         if fft_pows<500:
#             fund_freq.append(fund_freq[i])
#
#     fund_freq = fft_freqs[fft_pows<500]
#     noised_indices = np.where(fft_freqs  in fund_freq)
#     filter_fft = complex_ary.copy()
#     filter_fft[noised_indices] = 0  # 噪声数据位置 =0
#     filter_pow = np.abs(filter_fft)
#
def sl_filter(noised_signal):
    a=np.array((1,1,1))
    noised_signal.reshape(noised_signal.shape[0],1)
    if np.ndim(noised_signal)==1:
        filter_signal = np.zeros(noised_signal.shape)
    else:
        filter_signal = np.zeros(noised_signal.shape)
    for i in range(len(noised_signal)):
        if i ==0 or i==1 or i ==len(noised_signal)-1 or i ==len(noised_signal)-2:
            filter_signal[i]=noised_signal[i]
        else:
            filter_signal[i,]=float((noised_signal[i-2,]+noised_signal[i-1,]+noised_signal[i,]+noised_signal[i+1,]+noised_signal[i+2,])/5.0)
    return filter_signal

def sl_filter_imp(noised_signal):
    noised_signal.reshape(noised_signal.shape[0],1)
    if np.ndim(noised_signal)==1:
        filter_signal = np.zeros(noised_signal.shape)
    else:
        filter_signal = np.zeros(noised_signal.shape)
    for i in range(len(noised_signal)):
        if i ==0 or i==1 or i ==len(noised_signal)-1 or i ==len(noised_signal)-2:
            filter_signal[i]=noised_signal[i]
        else:
            filter_signal[i,]=(0.1*noised_signal[i-2,]+0.1*noised_signal[i-1,]+0.6*noised_signal[i,]+0.1*noised_signal[i+1,]+0.1*noised_signal[i+2,])
    return filter_signal

def ideal_lh_pass_filter(method,noised_signs,f0,sample_rate):
    """
    :param method: low or high 低通还是高通
    :param noised_siganl: 加噪信号(时域)
    :param f0: 截止频率
    :return: 去噪信号(频域)
    """
    times = np.arange(noised_signs.shape[0]) / sample_rate
    fft_filter = nf.fft(noised_signs)
    fft_freq = nf.fftfreq(noised_signs.size, times[1]-times[0])
    fft_pows = np.abs(fft_filter)
    if method == "low":
        # for i in range(len(noised_signs)):
        #     if abs(fft_freq[i])>f0:
        #             fft_filter[i]=0
        #     # where函数寻找那些需要抹掉的复数的索引
        noised_indices = np.where(abs(fft_freq) >= f0)
        fft_pows[noised_indices]=0
        fft_filter[noised_indices] = 0


    elif method == "high":
        for i in range(len(noised_signs)):
            if fft_freq[i] < f0:
                fft_filter[i] = 0
                fft_freq[i]= 0
                fft_pows[i] = 0

    #filter_sign=nf.ifft(fft_filter)
    return fft_filter


def Butterworth_filter(n,noised_signs,Wn,method):
    b, a = ss.butter(n, Wn, method)
    filter_sign = ss.filtfilt(b, a, noised_signs)
    return  filter_sign


def Spectral_subtraction_filter_easy(noised_signs,clear_noised_stime,clear_noised_etime,sample_rate):
    alpha = 1
    beta = 0
    start = (int)(clear_noised_stime*sample_rate-1)
    end = (int)(clear_noised_etime*sample_rate-1)
    sample_sign = noised_signs[start:end]
    fft_noised = nf.fft(noised_signs)
    fft_sample = nf.fft(sample_sign)
    fft_sample_pows= np.abs(fft_sample)
    fft_filter = np.zeros(len(noised_signs), dtype=np.complex)
    noised_spectral_average_value = complex(np.sum(fft_sample_pows)/len(fft_sample_pows))
    noised_indices = np.where(abs(fft_noised) >= alpha*noised_spectral_average_value)
    for i in range(len(fft_noised)):
        if(abs(fft_noised[i])>alpha*abs(noised_spectral_average_value)):
            if(fft_noised[i]>0):
                fft_filter[i]=  fft_noised[i] - alpha*abs(noised_spectral_average_value)
            elif(fft_noised[i]<0):
                fft_filter[i] = fft_noised[i] + alpha*abs(noised_spectral_average_value)
            else:
                fft_filter[i] = fft_noised[i]
        else:
            fft_filter[i]=beta*fft_noised[i]
    # #filter_sign = nf.ifft(fft_filter)
    return fft_filter,sample_sign

def Spectral_subtraction_filter_Berouti(noised_signs,clear_noised_stime,clear_noised_etime,sample_rate):
    times = np.arange(noised_signs.shape[0]) / sample_rate
    alpha = 4
    beta = 0.01
    start = (int)(clear_noised_stime*sample_rate-1)
    end = (int)(clear_noised_etime*sample_rate-1)
    sample_sign = noised_signs[start:end]
    fft_noised = nf.fft(noised_signs)
    fft_sample = nf.fft(sample_sign)
    fft_sample_pows= np.abs(fft_sample)
    fft_filter = np.zeros(len(noised_signs), dtype=np.complex)
    noised_spectral_average_value = complex(np.sum(fft_sample_pows)/len(fft_sample_pows))

    for i in range(len(fft_noised)):
        if(abs(fft_noised[i])>alpha*abs(noised_spectral_average_value)):
            if(fft_noised[i]>0):
                fft_filter[i]=  fft_noised[i] - alpha*abs(noised_spectral_average_value)
            elif(fft_noised[i]<0):
                fft_filter[i] = fft_noised[i] + alpha*noised_spectral_average_value
            else:
                fft_filter[i] = fft_noised[i]
        else:
            fft_filter[i]=beta*fft_noised[i]
    #filter_sign = nf.ifft(fft_filter)
    return fft_filter,sample_sign


