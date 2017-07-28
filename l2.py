#!/usr/bin/env python2
"""
Level 2 processing for DDC2 level1 data.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import numpy as np
import os
import pandas as pd


def parse_args():
    """Get command line arguments"""
    parser = ArgumentParser(
        description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--input_files', metavar='FILE', required=True,
        nargs='+', help='''Path(s) to file(s) containing level1 data'''
    )
    parser.add_argument(
        '-o', '--outfile', type=str, default='./data/test/l2.hd5',
        metavar='FILE', required=False,
        help='''Output location of level2 data'''
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='''Verbose'''
    )
    args = parser.parse_args()
    return args


def run(input_files, outfile, verbose):
    """Main function to perform level2 processing"""

    l_df = []
    for f in input_files:
        if verbose: print 'Opening {0}'.format(f)
        store = pd.HDFStore(f)
        df = store['df']
        if verbose: print df
        l_df.append(df)
        store.close()

    def m_concat(a, b):
        b['index'] += np.max(a['index']) + 1
        return pd.concat([a, b])

    l2_df = reduce(m_concat, l_df)
    print 'Number of waveforms = {0}'.format(len(l2_df['index'].unique()))

    store = pd.HDFStore(outfile)
    store['df'] = l2_df
    store.close()


def main():
    args = parse_args()
    run(
        input_files = args.input_files,
        outfile = args.outfile,
        verbose = args.verbose
    )

    print '=========='
    print 'DONE'
    print '=========='


main.__doc__ = __doc__


if __name__ == '__main__':
    main()
