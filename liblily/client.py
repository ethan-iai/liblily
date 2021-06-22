import argparse

from recognize import audio_recognize
from utils import open_audio, save_audios

noise_handler = {
	 
}

filter_handler = {

}

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="process piano audio samples")

	parser.add_argument('sample', help="path of audio sample")
	parser.add_argument('--noise', choices=[])
	parser.add_argument('--verbose', action="store_true", default=False)


	# def freq_recognize(y, sr, N=4, partial=0.85, delta=0.005, hop_length=512, slice=(0, 0.8), verbose=False):
	parser.add_argument('--partial', help="experience parameters in freqency recognition")
	parser.add_argument('--slice-min', help="left bound to slice beat frame")
	parser.add_argument('--slice-max', help="right bound to slice beat frame")
	parser.add_argument('-n', help='N of Butterworth filter')

	# add other arguments 

	args = parser.parse_args()
	
	name, y, sr = open_audio(args.sample)

	# noised_y = noise_handler[args.noise](y, args.verbose)
	# filtered_y = filter_handler[args.noise](y, args.verbose)

	_ = audio_recognize(y, sr, args.verbose)

	# TODO: output format unimplemented
	# for _, output in kwargs.items():
	# 	print(output)

	# save_audios(name, noised_y, filtered_y)


