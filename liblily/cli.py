import argparse
import os

import numpy as np
import scipy.signal as ss
import scipy.io.wavfile as wf

from liblily.recognize import audio_recognize
from liblily.noise import generate_sinusoid_2, awgn
from liblily.filter import ideal_lh_pass_filter, Butterworth_filter,\
						   sl_filter, Spectral_subtraction_filter_Berouti,\
						   Spectral_subtraction_filter_easy
from liblily.utils import open_audio, save_audios
from liblily.utils import get_src_path

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="process piano audio samples")

	parser.add_argument('sample', help="path of audio sample")
	parser.add_argument('--noise', choices=['high_freq', 'low_freq', 'guass'])
	parser.add_argument('--verbose', action="store_true", default=False)


	# def freq_recognize(y, sr, N=4, partial=0.85, delta=0.005, hop_length=512, slice=(0, 0.8), verbose=False):
	parser.add_argument('--partial', help="experience parameters in freqency recognition")
	parser.add_argument('--slice-min', help="left bound to slice beat frame")
	parser.add_argument('--slice-max', help="right bound to slice beat frame")
	parser.add_argument('-n', help='N of Butterworth filter')

	# add other arguments 

	args = parser.parse_args()
	
	name, y, sr = open_audio(args.sample)

	_ = audio_recognize(y, sr, args.verbose)

	sample_rate, origin_signs = wf.read(args.sample)

	times = np.arange(origin_signs.shape[0]) / sample_rate
	origin_signs=np.array(origin_signs)
	origin_signs=np.sum(origin_signs,axis = 1)/2 #双声道转单声道
	noised_signs=origin_signs.copy()
	filter_signs=origin_signs.copy()
	fft_filter=origin_signs.copy()

	# if not os.path.exists('~/.liblily'):
	# 	print('hey')
	# 	os.makedirs('~/.liblily')

	if args.noise == 'high_freq':
		noised_signs = noised_signs + generate_sinusoid_2(max(times) + times[1], 2000, 5000, sample_rate, 0)  # 高频
		noised_signs = noised_signs / (2 ** 15)
		origin_signs = origin_signs / (2 ** 15)
		fft_filter = ideal_lh_pass_filter("low", noised_signs, 3000, sample_rate)
		filter_signs = np.fft.ifft(fft_filter)

		wf.write(get_src_path('ideal_lh_pass_filter_noised_{}.wav'.format(name)), sample_rate, (filter_signs* 2 ** 15).astype(np.int16))
	
	elif args.noise == 'low_freq':
		noised_signs = noised_signs + generate_sinusoid_2(max(times)+times[1],2000,200,sample_rate,0) #低频
		noised_signs = noised_signs / (2 ** 15)
		origin_signs = origin_signs / (2 ** 15)
		filter_signs = Butterworth_filter(4, noised_signs, [(2 * 250 / sample_rate), (2 * 3000 / sample_rate)],"bandpass")
		fft_filter = np.fft.fft(filter_signs)

		wf.write(get_src_path('Butterworth_filter_noised_{}.wav'.format(name)), sample_rate, (filter_signs* 2 ** 15).astype(np.int16))

	elif args.noise == 'guass':
		noised_signs, noisy = awgn(origin_signs, snr=0, out='both', method='vectorized', axis=0)
		noised_signs = noised_signs / (2 ** 15)
		origin_signs = origin_signs / (2 ** 15)
		# 均值滤波器
		filter_signs= sl_filter(noised_signs)
		fft_filter = np.fft.fft(filter_signs)

		wf.write(get_src_path('sl_filter_noised_{}.wav'.format(name)), sample_rate, (filter_signs* 2 ** 15).astype(np.int16))

	else:
		raise NotImplementedError()
	
	wf.write(get_src_path('noised_{}.wav'.format(name)), sample_rate, (noised_signs* 2 ** 15).astype(np.int16))

	# TODO: output format unimplemented
	# for _, output in kwargs.items():
	# 	print(output)

	# save_audios(name, noised_y, filtered_y)

