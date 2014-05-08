import platform
from os import system, path

def flush():
    os = platform.system()

    if os == "Windows" or os.startswith("CYGWIN_NT"):
        dn = path.dirname(path.realpath(__file__))
        fn = path.join(dn, "data", "Flush.exe")
        system(fn)
    elif os == "Darwin":
        system("purge")
    elif os == "Linux":
        system("sync && echo 3 > /proc/sys/vm/drop_caches")
    else:
        print "Warning: Platform not supported"


if __name__ == "__main__":
    flush()
