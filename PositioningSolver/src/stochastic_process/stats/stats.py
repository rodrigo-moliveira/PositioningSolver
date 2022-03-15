import numpy as np
import math

from matplotlib import pyplot as plt
from scipy import signal


def power_spectral_density(x, fs):

    f, psd = signal.welch(x, fs=fs, return_onesided=True, scaling="density", nfft=1024, axis=0)
    # f, psd = signal.periodogram(x, fs=fs, return_onesided=True, scaling="density", nfft=1024, axis=0)

    return psd, f


def _get_taus(n, ts):
    max_sample_per_bin = int(math.floor(n / 9.0))  # max samples in one bin, at least 9 bins required

    if max_sample_per_bin * ts < 1:  # not enough data
        return [], []
    multiplier = []
    nextpow10 = math.ceil(math.log10(max_sample_per_bin))
    scale = 0.1
    for i in range(0, nextpow10):
        scale *= 10
        for j in range(1, 10):
            tmp = int(j * scale)
            if tmp <= max_sample_per_bin:
                multiplier.append(tmp)
            else:
                break

    # fill the tau array
    n_tau = len(multiplier)
    tau = np.zeros((n_tau,))
    for i in range(0, n_tau):
        n_sample_per_bin = multiplier[i]             # number of samples per bin

        tau[i] = n_sample_per_bin * ts

    return multiplier, tau


def allan_variance(x, fs):
    _n, _axes = x.shape  # time samples x dimension of x

    ts = 1.0 / fs  # observation period (time between samples)

    # get number of sampling taus to compute the allan variance
    multiplier, tau = _get_taus(_n, ts)
    n_tau = len(multiplier)

    a_var = np.zeros((n_tau, _axes))

    for j in range(_axes):
        a_var[:, j] = _allan_variance(x[:, j].flatten(), multiplier)

    return a_var, tau


def _allan_variance(x, multiplier):

    n_tau = len(multiplier)
    n = len(x)
    a_var = np.zeros((n_tau,))

    # calculate Allan variance
    for i in range(0, n_tau):
        n_sample_per_bin = multiplier[i]             # number of samples per bin
        n_bins = int(math.floor(n/n_sample_per_bin))  # number of bins
        if n_bins < 9:
            break

        # reshape data from [x0, x1, ..., xN] to [[x0,...xn], [x_n+1, ..., x_2n]], where the data is separated in bins
        # of length n_sample_per_bin
        tmp = np.reshape(x[0: n_bins*n_sample_per_bin], (n_bins, n_sample_per_bin))

        # compute the mean value inside each bin
        tmp = np.mean(tmp, 1)

        # compute the difference
        diff = tmp[1::] - tmp[0:-1]

        # Allan variance formula
        a_var[i] = 0.5 / (n_bins - 1) * np.sum(diff * diff)

    return a_var
