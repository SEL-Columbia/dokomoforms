#!/usr/bin/env python
#
# python -m cProfile -o /tmp/prof benchmark/benchmark_application_{section}.py
# python -m pstats /tmp/prof
# % sort time
# % stats 20

from argparse import ArgumentParser

import something
import dokomoforms.db

connection = dokomoforms.db.engine.connect()


def get_args():
    parser = ArgumentParser(description='Benchmark a function.')
    parser.add_argument('-n', '--num_runs', type=int, default=100,
                        help='The number of executions.')
    return parser.parse_args()


def main():
    args = get_args()
    parameters = None  # fill something in
    for _ in range(args.num_runs):
        something.do(connection, parameters)

if __name__ == '__main__':
    main()
