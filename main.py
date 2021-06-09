import argparse
import logging

from utils import open_voice, save_voices

noise_handler = {
	 
}

filter_handler = {

}

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="process voice samples")

	parser.add_argument('sample', help="path of voice sample")
	parser.add_argument('--noise', choices=[])
	parser.add_argument('--verbose', action='store_true', default=False)

	# add other arguments 

	args = parser.parse_args()

	logger = logging.basicConfig(level=logging.info)
	if args.verbose:
		pass
		
	name, voice = open_voice(args.sample)

	noised_voice = noise_handler[args.noise](voice)
	filtered_voice = filter_handler[args.noise](voice)

	kwargs = voice_recognize()

	# TODO: output format unimplemented
	print("".format(**kwargs))

	save_voices(name, noised_voice, filtered_voice)


