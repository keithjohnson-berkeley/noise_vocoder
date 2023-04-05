# Noise vocoder 

The main functions in the module are two that can be used to define a filter bank:

**third_octave_bands(low = 100, high=5000)** -- Computes cutoff frequencies for 1/3 octave bands, for a bank of filters where the center frequencies of the filters are spaced one octave apart in the range from 'low' Hz, to 'high' Hz.


**shannon_bands(nc = 24, low = 70, high = 5000)** -- Computes cutoff frequencies for a bank of filters that splits the frequency range (low to high in Hz) into nc number of equally spaced channels on the log frequency scale.  Please note that high, must be less than the Nyquist frequency (at most fs/2 - 1).

And one that uses a filter bank so defined.

**vocode(x, bands, fs)** -- returns a noise vocoded version of the audio samples in x, using frequency bands designed by one of the 'bands()' functions, or any other definition of a bank of bandpass filters.  'fs' is the sampling frequency of the audio in x.


See the notebook **using_noise_vocoder.ipynb** for example usage.

-------------------


This module is an extension of the excellent vocoder notebook published by Alexandre Chabot-Leclerc ([@AlexChabotL](http://twitter.com/alexchabotl)).   https://github.com/achabotl/vocoder.git
 

## License

[  ![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/80x15.png)](http://creativecommons.org/licenses/by-sa/4.0/)  

Building a noise vocoder with Python by [Alexandre Chabot-Leclerc](http://twitter.com/alexchabotl) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

