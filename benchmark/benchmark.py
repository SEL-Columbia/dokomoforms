#!/usr/bin/env python
#
# From github.com/tornadoweb/tornado/blob/master/demos/benchmark/benchmark.py
# A simple benchmark of tornado's HTTP stack.
# Requires 'ab' to be installed.
#
# Running without profiling:
# benchmark/benchmark.py
# benchmark/benchmark.py --quiet --num_runs=5|grep 'Requests per second'
#
# Running with profiling:
#
# python -m cProfile -o /tmp/prof benchmark/benchmark.py --email={email}
# --token={token} --path={path} --post_file={file.json}
# python -m pstats /tmp/prof
# % sort time
# % stats 20

import random
import signal
import subprocess

from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application
from tornado.log import logging

from webapp import pages, config


# choose a random port to avoid colliding with TIME_WAIT sockets left over
# from previous runs.
define('min_port', type=int, default=8000)
define('max_port', type=int, default=8887)

# Increasing --n without --keepalive will eventually run into problems
# due to TIME_WAIT sockets
define('n', type=int, default=300)
define('c', type=int, default=25)
define('keepalive', type=bool, default=False)
define('quiet', type=bool, default=False)

# Repeat the entire benchmark this many times (on different ports)
# This gives JITs time to warm up, etc.  Pypy needs 3-5 runs at
# --n=15000 for its JIT to reach full effectiveness
define('num_runs', type=int, default=1)

define('ioloop', type=str, default=None)

define('path', type=str, default='/')
define('post_file', type=str)
define('email', type=str)
define('token', type=str)


def handle_sigchld(sig, frame):
    IOLoop.instance().add_callback_from_signal(IOLoop.instance().stop)


def main():
    logging.getLogger('tornado.access').propagate = False
    parse_command_line()
    if options.ioloop:
        IOLoop.configure(options.ioloop)
    for _ in range(options.num_runs):
        run()


def run():
    app = Application(pages, **config)
    port = random.randrange(options.min_port, options.max_port)
    app.listen(port, address='0.0.0.0')
    signal.signal(signal.SIGCHLD, handle_sigchld)
    args = ['ab']
    args.extend(['-n', str(options.n)])
    concurrency_level = min(options.c, options.n)
    args.extend(['-c', str(concurrency_level)])
    if options.post_file is not None:
        args.extend(['-p', options.post_file])
        args.extend(['-T', 'application/json'])
    if options.email is not None:
        args.extend(['-H', 'Email:{}'.format(options.email)])
    if options.token is not None:
        args.extend(['-H', 'Token:{}'.format(options.token)])
    if options.keepalive:
        args.append('-k')
    if options.quiet:
        # just stops the progress messages printed to stderr
        args.append('-q')
    args.append('http://127.0.0.1:{}{}'.format(port, options.path))
    subprocess.Popen(args)
    IOLoop.instance().start()
    IOLoop.instance().close()
    del IOLoop._instance
    assert not IOLoop.initialized()


if __name__ == '__main__':
    main()
