import os

def get_src_path(path):
    prefix = os.environ.get('VP_SRC_PATH')
    if not prefix:
        prefix = os.path.expanduser('~/.vp')
    return os.path.abspath(os.path.join(prefix, path)) 

def open_voice(voice_path):
    pass

def save_voice(voice, voice_path):
    pass

def save_voices(name, noised_voice, filterd_voice):
    # FIXME: expanded name not added 
    save_voice(get_src_path(noised_voice, (name + '_noised.')))
    save_voice(get_src_path(filterd_voice, (name + '_filtered.')))