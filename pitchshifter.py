#!python
##
# pitch-shifter-cli.py: Pitch Shifter Command Line Tool
# 
# Author(s): Chris Woodall <chris@cwoodall.com>
# BSD License 2015 (c) Chris Woodall <chris@cwoodal.com>
##
import argparse
import numpy as np
import scipy
import scipy.interpolate
import scipy.io.wavfile
import sys
import logging
from resampler import *
from stft import *
from utilities import *
from version import *
from vocoder import *

logging.basicConfig(filename='pitchshifter-cli.log', filemode='w', level=logging.DEBUG)


def main(source, out, pitch, blend, chunk_size, overlap, debug, no_resample):
    # Try to open the wav file and read it
    print "source- {}, out- {}, pitch- {}, blend- {}, chunk_size- {}, overlap- {}, debug- {},no_resample- {}".format(source, out, pitch, blend, chunk_size, overlap, debug, no_resample)
    try:
        source = scipy.io.wavfile.read(source)
    except:
        print("File {0} does not exist".format(source))
        sys.exit(-1)

    RESAMPLING_FACTOR = 2 ** (pitch / 12)
    HOP = int((1 - overlap) * chunk_size)
    HOP_OUT = int(HOP * RESAMPLING_FACTOR)

    audio_samples = source[1].tolist()

    rate = source[0]
    mono_samples = stereoToMono(audio_samples)
    frames = stft(mono_samples, chunk_size, HOP)
    vocoder = PhaseVocoder(HOP, HOP_OUT)
    adjusted = [frame for frame in vocoder.sendFrames(frames)]

    merged_together = istft(adjusted, chunk_size, HOP_OUT)

    if no_resample:
        final = merged_together
    else:
        resampled = linear_resample(merged_together,
                                    len(mono_samples))
        final = resampled * blend + (1 - blend) * mono_samples

    output = scipy.io.wavfile.write(out, rate, np.asarray(final, dtype=np.int16))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Shifts the pitch of an input .wav file")
    parser.add_argument('--source', '-s', help='source .wav file', required=True)
    parser.add_argument('--out', '-o', help='output .wav file', required=True)
    parser.add_argument('--pitch', '-p', help='pitch shift', default=0, type=float)
    parser.add_argument('--blend', '-b', help='blend', default=1, type=float)
    parser.add_argument('--chunk-size', '-c', help='chunk size', default=4096, type=int)
    parser.add_argument('--overlap', '-e', help='overlap', default=.9, type=float)
    parser.add_argument('--debug', '-d', help='debug flag', action="store_true")
    parser.add_argument('--no-resample', help='debug flag', action="store_true")

    args = parser.parse_args()
    
    source = args.source
    out = args.out
    pitch = args.pitch
    blend = args.blend
    chunk_size = args.chunk_size
    overlap = args.overlap
    debug = args.overlap
    no_resample = args.no_resample
    
    main(source, out, pitch, blend, chunk_size, overlap, debug, no_resample)

