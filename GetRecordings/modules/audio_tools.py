import soundfile
import numpy as np
import json
import itertools
import pydub

def read_audio(path: str):
    '''
    Uses soundfile to read a PCM file and returns
    a numpy array containing samples and the sample rate

    Input arguments:
    * path (str='./data/f1.wav'): A path to a .wav file
    '''
    return soundfile.read(path)

def save_audio(wave: np.ndarray, sr: int, path: str):
    '''
    Save a waveform to file using soundfile
    Input arguments:
    * wave (np.ndarray): An array carrying the waveform
    * sr (int): The sample rate of the signal
    * path (str): Where the new file will be stored
    '''
    soundfile.write(path, wave, sr)

def dump_json(item, path: str):
    with open(path, 'w', encoding='utf-8') as json_f:
        json.dump(item, json_f, ensure_ascii=False, indent=4)

def get_audio_info(path: str, verbose:bool = False):
    '''
    Uses soundfile to read a PCM file and returns
    an object with information about a SoundFile
    '''
    return soundfile.info(path, verbose)

def get_duration(wave: np.ndarray, sr):
    '''
    Returns the duration of the recording
    '''
    duration = len(wave) / sr
    return float("{0:.2f}".format(duration))


""" def down_sample(wave: np.ndarray, orginal_sr, resample_sr):
    '''
    Takes in a wave, orginal sample rate and the desired sample rate 
    Returns a resampled wave form.
    '''

    if resample_sr > orginal_sr:
        input(f'Warning you are about to upsample from\n{orginal_sr} to {resample_sr}. Are you sure you want to continue?')
    return librosa.resample(wave, orginal_sr, resample_sr)
 """
def get_bit_depth(path: str):
    '''
    Bit-depth: The higher the bit-depth, the more dynamic range can be captured. 
    Dynamic range is the difference between the quietest and loudest volume of an instrument, 
    part or piece of music. A typical value seems to be 16 bit or 24 bit. A bit-depth of 16 bit has 
    a theoretical dynamic range of 96 dB, whereas 24 bit has a dynamic range of 144 dB (source).
    '''
    ob = soundfile.SoundFile(path)
    return ob.subtype


def get_samplerate(path: str):
    '''
    Sample rate: Audio signals are analog, but we want to represent them digitally. Meaning we 
    want to discretize them in value and in time. The sample rate gives how many times per 
    second we get a value. The unit is Hz. The sample rate needs to be at least double of the
    highest frequency in the original sound, otherwise you get aliasing.
    '''
    ob = soundfile.SoundFile(path)
    return ob.samplerate

def get_channels(path: str):
    '''
    Returns the count of channels
    '''
    ob = soundfile.SoundFile(path)
    return ob.channels

    
def detect_empty_waves(path:str):
    '''
    Returns true if the wave file is empty
    '''
    wave = pydub.AudioSegment.from_wav(path)
    if pydub.silence.detect_silence(wave):
        return False
    else:
        return True

def db_to_float(db, using_amplitude=True):
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    db = float(db)
    if using_amplitude:
        return 10 ** (db / 20)
    else:  # using power
        return 10 ** (db / 10)

def detect_silence(audio_segment, min_silence_len=1000, silence_thresh=-16, seek_step=1):
    seg_len = len(audio_segment)

    # you can't have a silent portion of a sound that is longer than the sound
    if seg_len < min_silence_len:
        return False

    # convert silence threshold to a float value (so we can compare it to rms)
    silence_thresh = db_to_float(silence_thresh) * audio_segment.max_possible_amplitude

    # find silence and add start and end indicies to the to_cut list
    silence_starts = []

    # check successive (1 sec by default) chunk of sound for silence
    # try a chunk at every "seek step" (or every chunk for a seek step == 1)
    last_slice_start = seg_len - min_silence_len
    slice_starts = range(0, last_slice_start + 1, seek_step)

    # guarantee last_slice_start is included in the range
    # to make sure the last portion of the audio is searched
    if last_slice_start % seek_step:
        slice_starts = itertools.chain(slice_starts, [last_slice_start])

    for i in slice_starts:
        audio_slice = audio_segment[i:i + min_silence_len]
        if audio_slice.rms <= silence_thresh:
            silence_starts.append(i)

    # short circuit when there is no silence
    if not silence_starts:
        return []

    # combine the silence we detected into ranges (start ms - end ms)
    silent_ranges = []

    prev_i = silence_starts.pop(0)
    current_range_start = prev_i

    for silence_start_i in silence_starts:
        continuous = (silence_start_i == prev_i + seek_step)

        # sometimes two small blips are enough for one particular slice to be
        # non-silent, despite the silence all running together. Just combine
        # the two overlapping silent ranges.
        silence_has_gap = silence_start_i > (prev_i + min_silence_len)

        if not continuous and silence_has_gap:
            silent_ranges.append([current_range_start,
                                  prev_i + min_silence_len])
            current_range_start = silence_start_i
        prev_i = silence_start_i

    silent_ranges.append([current_range_start,
                          prev_i + min_silence_len])

    return silent_ranges
