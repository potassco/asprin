import os
import tempfile


BASE  = "base"
EMPTY = ""

# check pp_parser for an usage example
class Capturer:

    def __init__(self,stdx):
        self.__original_fd      = stdx.fileno()
        self.__save_original_fd = os.dup(self.__original_fd)
        self.__tmp_file         = tempfile.TemporaryFile()
        os.dup2(self.__tmp_file.fileno(),self.__original_fd)

    def read(self):
        self.__tmp_file.flush()
        self.__tmp_file.seek(0)
        return self.__tmp_file.read()

    def close(self):
        os.dup2(self.__save_original_fd,self.__original_fd)
        os.close(self.__save_original_fd)
        self.__tmp_file.close()

class SilentException(Exception):
    pass

class FatalException(Exception):
    pass
