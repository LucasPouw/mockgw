from astropy.cosmology import z_at_value
import matplotlib.pyplot as plt
import numpy as np
from astropy.cosmology.core import CosmologyError
import sys


def make_nice_plots():
    # We define some properties for the figures
    import matplotlib as mpl
    SMALL_SIZE = 10 * 2 
    MEDIUM_SIZE = 12 * 2
    BIGGER_SIZE = 14 * 2

    plt.rc('text', usetex=True)
    plt.rc('axes', titlesize=SMALL_SIZE)                     # fontsize of the axes title\n",
    plt.rc('axes', labelsize=MEDIUM_SIZE)                    # fontsize of the x and y labels\n",
    plt.rc('xtick', labelsize=SMALL_SIZE, direction='out')   # fontsize of the tick labels\n",
    plt.rc('ytick', labelsize=SMALL_SIZE, direction='out')   # fontsize of the tick labels\n",
    plt.rc('legend', fontsize=SMALL_SIZE)                    # legend fontsize\n",
    mpl.rcParams['axes.titlesize'] = BIGGER_SIZE
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['mathtext.fontset'] = 'cm'
    mpl.rcParams['font.family'] = 'STIXgeneral'

    mpl.rcParams['figure.dpi'] = 100

    mpl.rcParams['xtick.minor.visible'] = True
    mpl.rcParams['ytick.minor.visible'] = True
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams['ytick.right'] = True

    mpl.rcParams['xtick.major.size'] = 10
    mpl.rcParams['ytick.major.size'] = 10
    mpl.rcParams['xtick.minor.size'] = 4
    mpl.rcParams['ytick.minor.size'] = 4

    mpl.rcParams['xtick.major.width'] = 1.25
    mpl.rcParams['ytick.major.width'] = 1.25
    mpl.rcParams['xtick.minor.width'] = 1
    mpl.rcParams['ytick.minor.width'] = 1


def uniform_shell_sampler(rmin, rmax, n_samps):
    theta = np.arccos(np.random.uniform(size=n_samps, low=-1, high=1))  # cosine is uniformly distributed between -1 and 1
    phi = 2 * np.pi * np.random.uniform(size=n_samps) - np.pi  # Draws phi from -np.pi to np.pi
    r = ( np.random.uniform(size=n_samps, low=rmin**3, high=rmax**3) )**(1/3)
    return r, theta, phi


def spherical2cartesian(r, theta, phi):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return x, y, z


def cartesian2spherical(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(np.clip(z / r, -1, 1))  # From 0 to pi
    phi = np.arctan2(y, x)  # From -pi to pi
    return r, theta, phi


def fast_z_at_value(function, values, num=10000):
    try:
        zmin = z_at_value(function, values.min())
    except CosmologyError:
        sys.exit(values.min(), 'THIS DISTANCE GAVE AN ERROR, FIX THAT')
    zmax = z_at_value(function, values.max())
    zgrid = np.geomspace(zmin, zmax, num)
    valgrid = function(zgrid)
    zvals = np.interp(values.value, valgrid.value, zgrid)
    return zvals.value


def check_equal(a, b):
    if len(a) != len(b):
        return False
    return sorted(a) == sorted(b)


if __name__ == '__main__':

    import matplotlib.pyplot as plt
    from astropy.cosmology import FlatLambdaCDM
    import astropy.units as u
    import scipy.stats as stats
    from scipy.optimize import root_scalar
    from scipy.special import erf

    cosmo = FlatLambdaCDM(H0=67.9, Om0=0.3065)

    cl = 0.999
    sig = 500
    sig2 = 1
    xyz_true = np.array([[5000, 3000, 1000], [10, 10, 10]])
    std = np.array([[sig, sig, sig], [sig2, sig2, sig2]])

    def cl_volume_from_sigma(cl, sigmas):
        '''Calculates length of CL% vector when x, y, z are normally distributed with the same sigma'''
        radii = np.zeros(len(sigmas))
        for i, sigma in enumerate(sigmas):
            vector_length_cdf = lambda x: erf(x / (sigma * np.sqrt(2))) - np.sqrt(2) / (sigma * np.sqrt(np.pi)) * x * np.exp(-x**2 / (2 * sigma**2)) - cl
            radii[i] = root_scalar(vector_length_cdf, bracket=[0, 100 * sigma], method='bisect').root
        return 4 * np.pi * radii**3 / 3

    xyz_meas = np.random.normal(loc=xyz_true, scale=std, size=(2, 3))
    print(xyz_meas)
    volumes = cl_volume_from_sigma(cl, np.array([sig, sig2]))
    print(volumes)

    # r, theta, phi = cartesian2spherical(x, y, z)

    # z = fast_z_at_value(cosmo.comoving_distance, r * u.Mpc)

    # fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
    # ax[0,0].hist(r, density=True, bins=30)
    # ax[0,1].hist(np.cos(theta), density=True, bins=30)
    # ax[1,0].hist(phi, density=True, bins=30)
    # ax[1,1].hist(z, density=True, bins=30)
    # ax[0,0].set_xlabel('r com [Mpc]')
    # ax[0,1].set_xlabel('theta [rad]')
    # ax[1,0].set_xlabel('phi [rad]')
    # ax[1,1].set_xlabel('z')
    # plt.tight_layout()
    # plt.savefig('test.pdf')
    # plt.show()