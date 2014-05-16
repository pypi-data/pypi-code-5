'''
Created on Dec 2, 2013

@author: Wang
'''
from IPython.core.display import Image
import factoracle as fa
import Resources.generate as ge
import os

def main():

    filename = os.path.abspath('') + '/FunkBass.wav'
    outfilename = os.path.abspath('') + '/audio_generate_test.wav'
    todo = ['chroma'] 
    buffer_size = 4096 * 4
    hop = buffer_size / 2
    features = fa.make_features(filename, buffer_size, hop, todo)
    
    thresholds = (0.001, 2.0, 0.01)
    ideal_t = fa.calculate_ideal_threshold(thresholds, features, 'chroma')
    thresh =ideal_t[0][1]
    oracle = fa.make_oracle(thresh, 'a', features, 'chroma')
    
    fs = 44100
    duration = 20 * fs / hop
    ge.generate_audio(filename, 
                       outfilename, 
                       buffer_size, 
                       hop, oracle, 
                       duration, 
                       0.25, 0, 1)
                    
if __name__ == '__main__':
    main()