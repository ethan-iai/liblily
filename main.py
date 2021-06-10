import argparse

from recognize import voice_recognize
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

	parser.add_argument('--partial', help="experience parameters in freqency recognition")

	# add other arguments 

	args = parser.parse_args()
	
	name, y, sr = open_audio(args.sample)

	noised_y = noise_handler[args.noise](y, args.verbose)
	filtered_y = filter_handler[args.noise](y, args.verbose)

	kwargs = voice_recognize(y, sr, args.verbose)

	# TODO: output format unimplemented
	for _, output in kwargs.items():
		print(output)

	save_audios(name, noised_y, filtered_y)


