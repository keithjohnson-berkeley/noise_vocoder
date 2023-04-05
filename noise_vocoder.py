'''This module is based on the excellent vocoder notebook published by Alexandre Chabot-Leclerc ([@AlexChabotL](http://twitter.com/alexchabotl)).   https://github.com/achabotl/vocoder.git

I added the "Shannon" vocoding scheme and altered some of the functions to be a little more general. I also converted the filtering to use sos coefficients, which improved the numerical stability of the code.  Keith Johnson
'''

import numpy as np
import scipy as sp

def design_filter(bounds, fs, order=4):
    ''' Use scipy.signal.butter() to design a Butterworth bandpass filter.

        inputs:
            -- bounds: the lower bound, upper bound of a bandpass filter
            -- fs: sampling frequency of the audio
        
        output:
            -- sos filter coefficients of the bandpass filter

    '''
    return sp.signal.butter(order, bounds, fs=fs, btype='bandpass', output='sos')

def third_octave_bounds(cf):
    ''' Return the upper and lower frequency bounds for a 
        1/3 octave filter around a center frequency.
        
        input:
            -- cf: a center frequency (Hz)
    
        output:
            -- an array of two values, the upper and lower bound of the filter
    '''
    third_octave_ratio = 2 ** (1/6)  # 2 * 1/6 = 1/3
    return np.array([cf / third_octave_ratio, cf * third_octave_ratio])

def octave_spaced_frequencies(low, high):
    ''' Get octave spaced-center frequencies between low and high.  The first 
    is equal to 'low' and the remainder are twice the previous one on the list.
    
        inputs:
            -- low: the lowest center frequency
            -- high: the upper bound for center frequencies
        output:
            -- an array of center frequencies
    '''
    number_of_octaves = np.log2(high) - np.log2(low)
    return low * 2 ** np.arange(number_of_octaves)

def third_octave_bands(low = 100, high=5000):
    '''Compute cutoff frequencies for 1/3 octave bands, the centers are spaced
    one octave apart
        inputs: 
            -- low: the lowest filter center frequency
            -- high: the upper bound for center frequencies
        output:
            -- an array of low,high frequency pairs, one pair for each 
                bandpass filter in a filter bank
    '''
    center_frequencies = octave_spaced_frequencies(low, high)
    return[third_octave_bounds(cf) for cf in center_frequencies]

def amplitude_envelope(x, fs, cutoff=30, order=2,):
    ''' Get amplitude envelope of x (half-wave rectification, lowpass filtered)
        inputs:
            -- x: audio samples in a 1-D numpy array
            -- fs: the sampling frequency of the sound to be filtered
            -- cutoff:  cutoff freq. for low-pass filter (default: 30Hz)
            -- order: order of the Butterworth low-pass filter (default: 2)
        output:
            -- amplitude envelope, same number of samples as x
    '''
    envelope = np.abs(x)
    coefs = sp.signal.butter(order, cutoff * 2 / fs, output='sos')
    low_pass_filtered_envelope = sp.signal.sosfiltfilt(coefs, envelope)
    return low_pass_filtered_envelope

def shannon_bands(nc = 24, low = 70, high = 5000):
    ''' take a range from low freq to high freq and split it into nc 
    (number of channels) frequency bands on log freq scale
    
        inputs:
            -- nc: number of channels
            -- low: low freq of range covered by the channels (Hz)
            -- high: high freq of range covered by the channels (at most fs/2 - 1)
        output:
            -- array of bands (low,high) for a bank of bandpass filters
    '''
    freqs = np.exp(np.linspace(np.log(low), np.log(high), num=nc+1))
    return [(freqs[i],freqs[i+1]) for i in range(nc)]


def apply_filterbank(x, bands, fs):
    ''' Filter using scipy.signal.sosfiltfilt(), in a bank of bandpass filters.
        
        inputs: 
            -- x:  audio samples in a 1-D numpy array
            -- bands: An array of n filter lower/upper cut off freq pairs (n,2)
            -- fs: the sampling frequency of the sound to be filtered
        output: 
            -- y: a 2-D array of x filtered by each band
                    y[0] is x filtered by bands[0]
    '''
    n_samples = x.shape[-1]
    n_channels = len(bands)
    
    # this line makes coefficients for the filter bank
    filterbank = [design_filter(b, fs,order=8) for b in bands]
    y = np.zeros((n_channels, n_samples))
    for idx, coefs in enumerate(filterbank):
        y[idx] = sp.signal.sosfiltfilt(coefs, x)  # filter each band
    return y

def vocode(x, bands, fs):
    ''' Noise vocoding - replace sound with bandpassed noise, using a 
        bank of filters defined by bands.
        
        input: 
            -- x:  audio samples in a 1-D numpy array
            -- bands: An array of n bandpass filter lower/upper cut off freqs (n,2)
            -- fs: the sampling frequency of the sound to be filtered
        output:
            -- an array of samples, the name length as x
    '''
    n_channels = len(bands)
    n_samples = x.shape[-1]
    noise = np.random.randn(n_samples) 

    filtered_x = apply_filterbank(x, bands, fs)
    filtered_noise = apply_filterbank(noise, bands, fs)
    
    vocoded_noise = np.zeros((n_channels, n_samples))
    for idx, (x_band, noise_band) in enumerate(zip(filtered_x, filtered_noise)):
        envelope = amplitude_envelope(x_band,fs)
        vocoded_noise[idx] = envelope * noise_band
    return np.sum(vocoded_noise, axis=0)