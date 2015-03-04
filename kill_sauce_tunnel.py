import subprocess
import signal
import os


def main():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if 'sc' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

if __name__ == '__main__':
    main()
