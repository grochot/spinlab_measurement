import numpy as np
def FFT_mean(fft_data):
	# obliczenie średniego sygnału FFT
    mag_spectrum = np.abs(fft_data)

# Compute the square of the magnitude spectrum
    mag_spectrum_squared = np.square(mag_spectrum)

# Compute the RMS value of the squared magnitude spectrum
    rms_value = np.sqrt(np.mean(mag_spectrum_squared))

# Divide the magnitude spectrum by the RMS value to obtain the RMS-averaged spectrum
    rms_spectrum = mag_spectrum / rms_value

    return rms_spectrum
 
 
