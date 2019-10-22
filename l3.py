#!/usr/bin/env python2
"""
Level 3 processing for DDC2 level2 data.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import numpy as np
import os
import pandas as pd
from scipy.optimize import curve_fit


def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


def cum_gauss(A, mu, sigma):
    return A*np.sqrt(2*np.pi)/(np.sqrt(1/np.power(sigma, 2)))


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--infile', type=str, required=True,
        help='''Path to file containing level2 data'''
    )
    parser.add_argument(
        '-o', '--outfile', type=str, default='./data/test/l3.hd5',
        metavar='FILE', required=False,
        help='''Output location of level3 data'''
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='''Verbose'''
    )
    args = parser.parse_args()
    return args


def run(infile, outfile, verbose):
    """Main function to perform level2 processing"""

    if verbose: print 'Opening {0}'.format(infile)
    store = pd.HDFStore(infile)
    df = store['df']
    if verbose: print df
    store.close()

    df['gauss_A'] = 0
    df['gauss_mu'] = 0
    df['gauss_sigma'] = 0
    df['gauss_int'] = 0

    p0 = [1., 120., 1.] # Initial guess.
    for idx in xrange(df['index'].max() + 1):
        if verbose: print 'Processing waveform index {0}'.format(idx)
        mask_idx = df['index'] == idx
        wv = df[mask_idx]
        wv_fp = wv[wv['isamp'] < 150]
        coeff, var_matrix = curve_fit(
            gauss, wv_fp['isamp'], wv_fp['voltage'], p0=p0,
            bounds=([0, 0, 0], [9999, 9999, 9999])
        )
        A, mu, sigma = coeff
        df.ix[mask_idx, 'gauss_A'] = A
        df.ix[mask_idx, 'gauss_mu'] = mu
        df.ix[mask_idx, 'gauss_sigma'] = sigma

        gauss_int = cum_gauss(*coeff) / 1e3 # convert to nVs
        df.ix[mask_idx, 'gauss_int'] = gauss_int

    if verbose: print 'Finished processing'
    if verbose: print df

    if ((df['gauss_A'] == 0) | (df['gauss_mu'] == 0) | (df['gauss_sigma'] == 0)).any():
        print df
        raise AssertionError

    if verbose: print 'Saving to {0}'.format(outfile)
    store = pd.HDFStore(outfile)
    store['df'] = df
    store.close()


def main():
    args = parse_args()
    run(
        infile = args.infile,
        outfile = args.outfile,
        verbose = args.verbose
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()

