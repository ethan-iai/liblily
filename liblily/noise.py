import numpy as np
import numpy.fft as nf
import scipy.signal as ss
import scipy.io.wavfile as wf
import matplotlib.pyplot as mp

def awgn(x, snr, out='signal', method='vectorized', axis=0):
    # Signal power
    if method == 'vectorized':
        N = x.size
        Ps = np.sum(x ** 2 / N)

    elif method == 'max_en':
        N = x.shape[axis]
        Ps = np.max(np.sum(x ** 2 / N, axis=axis))
    elif method == 'axial':
        N = x.shape[axis]
        Ps = np.sum(x ** 2 / N, axis=axis)
    else:
        raise ValueError('method \"' + str(method) + '\" not recognized.')

    # Signal power, in dB
    Psdb = 10 * np.log10(Ps)

    # Noise level necessary
    Pn = Psdb - snr

    # Noise vector (or matrix)
    n = np.sqrt(10 ** (Pn / 10)) * np.random.normal(0, 1, x.shape)
    if out == 'signal':
        return x + n
    elif out == 'noise':
        return n
    elif out == 'both':
        return x + n, n
    else:
        return x + n

def generate_sinusoid(N, A, f0, fs, phi):
    '''
    N(int) : number of samples =94322
    A(float) : amplitude       =1
    f0(float): frequency in Hz =15000
    fs(float): sample rate     =22050
    phi(float): initial phase  =0

    return
    x (numpy array): sinusoid signal which lenght is M
    '''

    T = 1 / fs
    n = np.arange(N)  # [0,1,..., N-1]
    x = A * np.sin(2 * f0 * np.pi * n * T + phi)

    return x


def generate_sinusoid_2(t, A, f0, fs, phi):
    '''
    t  (float) : time length of the generated sequence
    A  (float) : amplitude
    f0 (float) : frequency
    fs (float) : sample rate
    phi(float) : initial phase

    returns
    x (numpy array): sinusoid signal sequence
    '''

    T = 1.0 / fs
    N = t / T

    return generate_sinusoid(N, A, f0, fs, phi)


if __name__=='__main__':
    import matplotlib.pyplot as plt
    A = 0.5
    f0 = 5
    fs = 22050
    phi = 0
    t = 4
    x = generate_sinusoid_2(t, A, f0, fs, phi)
    n = np.arange(0, t, 1 / fs)
    plt.plot(n, x)
    plt.ylim(-1, 1)
    plt.xlabel('time(s)')
    plt.ylabel('amplitude')
    plt.title('True signal in time domain')
    plt.savefig('e_DFT1.eps', bbox_inches='tight')
    plt.show()
