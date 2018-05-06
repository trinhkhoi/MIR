import numpy as np
from indj_mir.com.indj.mir.services import HandleAudioFile as hd
from rp_extract import rp_extract
import h5py
import os
from scipy import stats
from scipy.spatial.distance import euclidean
from sklearn.cluster import KMeans


def concate_timbre_feature(song_name):
    result = []
    mfcc = hd.get_mfcc(song_name)
    spectral_contrast = hd.get_spectral_contrast(song_name)
    harmonic, percussive = hd.get_harmonic_percussive(song_name)
    args = (mfcc, spectral_contrast, harmonic, percussive)
    result = np.concatenate(args)
    print('len result: ', len(result))
    print('len result 0: ', len(result[0]))
    return result


def calculate_single_gaussian(data, song_name):
    print('data.shape: ', data.shape)
    data_transform = data.T
    mu = np.mean(data_transform, axis=0)
    print('mu.shape: ', mu.shape)
    sigma = np.cov(data_transform, rowvar=0)
    print('cor.shape: ', sigma.shape)

    if not os.path.exists('/data/hdf5s/'):
        os.makedirs('/data/hdf5s/')
    data_file = h5py.File('%s%s_gau.hdf5' % ('/data/hdf5s/', song_name), 'w')
    data_file.create_dataset('mu', data=np.asanyarray(mu))
    data_file.create_dataset('sigma', data=np.asanyarray(sigma))
    data_file.close()

    return np.asanyarray(mu), np.asanyarray(sigma)


def mix_gaussian(m1, v1, m2, v2):
    print('Start calculate mix ----------')
    m = 0.5*np.add(m1, m2)
    v = 0.5 * (v1 + m1*m1.T) + 0.5 * (v2 + m2*m2.T) - m*m.T

    return m, v

def gau_js(pm, pv, qm, qv):
    """
    Jensen-Shannon divergence between two Gaussians.  Also computes JS
    divergence between a single Gaussian pm,pv and a set of Gaussians
    qm,qv.
    Diagonal covariances are assumed.  Divergence is expressed in nats.
    """
    if (len(m2.shape) == 2):
        axis = 1
    else:
        axis = 0
        # Calculate mix gaussian
    m, v = mix_gaussian(pm, pv, qm, qv)
    print('m: ', m)
    print('v: ', v)
    print('pm.size: ', pm.size, pm[0].size)

    # Determinants of diagonal covariances pv, qv
    dpv = abs(pv)#.prod()
    dqv = abs(v)#.prod(axis)
    # Inverses of diagonal covariances pv, qv
    iqv = 1./v
    ipv = 1./pv
    # Difference between means pm, qm
    diff = m - pm
    # KL(p||q)
    kl1 = (0.5 *
           (np.log(dqv / dpv)            # log |\Sigma_q| / |\Sigma_p|
            + (iqv * pv).sum(axis)          # + tr(\Sigma_q^{-1} * \Sigma_p)
            + (diff.T * iqv * diff).sum(axis) # + (\mu_q-\mu_p)^T\Sigma_q^{-1}(\mu_q-\mu_p)
            - pm.size))                     # - N
    # KL(q||p)
    kl2 = (0.5 *
           (np.log(dpv / dqv)            # log |\Sigma_p| / |\Sigma_q|
            + (ipv * v).sum(axis)          # + tr(\Sigma_p^{-1} * \Sigma_q)
            + (diff.T * ipv * diff).sum(axis) # + (\mu_q-\mu_p)^T\Sigma_p^{-1}(\mu_q-\mu_p)
            - pm.size))                     # - N
    # JS(p,q)
    return 0.5 * (kl1 + kl2)


def gau_kl(pm, pv, qm, qv):
    """
    Kullback-Liebler divergence from Gaussian pm,pv to Gaussian qm,qv.
    Also computes KL divergence from a single Gaussian pm,pv to a set
    of Gaussians qm,qv.
    Diagonal covariances are assumed.  Divergence is expressed in nats.
    """
    if (len(qm.shape) == 2):
        axis = 1
    else:
        axis = 0
    # Determinants of diagonal covariances pv, qv
    dpv = abs(pv)#.prod()
    dqv = abs(qv)#.prod(axis)
    # Inverse of diagonal covariance qv
    iqv = 1./qv
    # Difference between means pm, qm
    diff = qm - pm
    return (0.5 *
            ((iqv * pv)#.sum(axis)          # + tr(\Sigma_q^{-1} * \Sigma_p)
             + (diff.T * iqv * diff)#.sum(axis) # + (\mu_q-\mu_p)^T\Sigma_q^{-1}(\mu_q-\mu_p)
             - np.log(dqv / dpv)  # log |\Sigma_q| / |\Sigma_p|
             - pm.size))
if __name__ == "__main__":

    song1 = '210013717313010895'
    song2 = '210013717313010883'

    # Calculate Timbre gaussian
    if not os.path.exists('/data/hdf5s/%s_gau.hdf5' % song1):
        data1 = concate_timbre_feature(song1)
        m1, v1 = calculate_single_gaussian(data1, song1)
    else:
        filename = '%s%s_gau.hdf5' % ('/data/hdf5s/', song1)
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            m1 = hf['mu'][:]
            v1 = hf['sigma'][:]

    if not os.path.exists('/data/hdf5s/%s_gau.hdf5' % song2):
        data2 = concate_timbre_feature(song2)
        m2, v2 = calculate_single_gaussian(data2, song2)
    else:
        filename = '%s%s_gau.hdf5' % ('/data/hdf5s/', song2)
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            m2 = hf['mu'][:]
            v2 = hf['sigma'][:]

    # Calculate Rhythm gaussian
    data_rhy_song1 = hd.get_rhythm(song1)
    data_rhy_song2 = hd.get_rhythm(song2)
    if not os.path.exists('/data/hdf5s/%s_gau_rhy.hdf5' % song1):
        m_rhy1 = np.mean(data_rhy_song1, axis=0)
        print('mu_rhy1: ', m_rhy1.shape)
        v_rhy1 = np.cov(data_rhy_song1, rowvar=0)
        print('v_rhy1: ', v_rhy1.shape)
        #m_rhy1, v_rhy1 = calculate_single_gaussian(data_rhy_song1, song1)
    else:
        filename = '%s%s_gau_rhy.hdf5' % ('/data/hdf5s/', song1)
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            m_rhy1 = np.asmatrix(hf['mu'][:])
            v_rhy1 = np.asmatrix(hf['sigma'][:])

    if not os.path.exists('/data/hdf5s/%s_gau_rhy.hdf5' % song2):
        m_rhy2 = np.mean(data_rhy_song2, axis=0)
        print('m_rhy2: ', m_rhy2.shape)
        v_rhy2 = np.cov(data_rhy_song2, rowvar=0)
        print('v_rhy2: ', v_rhy2.shape)
        # m_rhy2, v_rhy2 = calculate_single_gaussian(data_rhy_song2, song2)
    else:
        filename = '%s%s_gau_rhy.hdf5' % ('/data/hdf5s/', song2)
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            m_rhy2 = np.asmatrix(hf['mu'][:])
            v_rhy2 = np.asmatrix(hf['sigma'][:])

    median1 = np.median(data_rhy_song1)
    median2 = np.median(data_rhy_song2)

    # Calculate euclidean distance of rhythm features
    dist_rhy = euclidean(median1, median2)
    print('dist_rhy: ', dist_rhy)

    # Calculate Jensen Shannon Gaussian
    print('start calculate jensen shannon gaussian ----------')
    timbre_js = 0.5*(gau_kl(m1, v1, m2, v2) + gau_kl(m2, v2, m1, v1))
    #timbre_js = gau_js(m1, v1, m2, v2)
    print('timbre distance: ', timbre_js)
    #rhythm_js = gau_js(m_rhy1, v_rhy1, m_rhy2, v_rhy2)

    mu_avr = mu = np.mean(timbre_js, axis=0)
    print('mu_avr: ', mu_avr)
    print('\nStart calculate linear combination with z-score ---')
    #combine = 0.5*(stats.zscore(timbre_js) + dist_rhy)
    #print('result: ', combine)
