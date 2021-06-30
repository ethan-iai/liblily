import os
import librosa
import soundfile as sf

def get_src_path(path):
    prefix = os.environ.get('LIBLILY_SRC_PATH')
    if not prefix:
        prefix = os.path.expanduser('~/.vp')
    return os.path.abspath(os.path.join(prefix, path)) 


def open_audio(audio_path):
    audio, sr = librosa.load(audio_path, mono=True)
    tokens = os.path.basename(audio_path).split('.')
    
    return ''.join(tokens[:max(1, len(tokens) - 1)]),\
           audio, sr


def _save_audio(audio, audio_path):
    sf.write(audio_path, audio, sr, subtype='PCM_24')
    

def save_audios(name, noised_audio, filterd_audio):
    _save_audio(get_src_path(noised_audio, 'noised_{}.wav'.format(name)))
    _save_audio(get_src_path(filterd_audio, 'filtered_{}.wav'.format(name)))


if __name__ == '__main__':
    name, y, sr = open_audio('demo.wav')
    