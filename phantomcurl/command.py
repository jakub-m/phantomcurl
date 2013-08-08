import subprocess
import threading


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self._communicated = ('', '')

    def run(self, timeout):
        '''timeout is in seconds, fractions accepted'''
        def target():
            self.process = subprocess.Popen(
                self.cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            self._communicated = self.process.communicate()
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self._communicated


def call(command, timeout=None):
    '''timeout in seconds. Returns (out, err) for the executed command'''
    assert (isinstance(timeout, (int, float)) or
            timeout is None), timeout.__class__
    cmd = Command(command)
    return cmd.run(timeout)
