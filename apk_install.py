from os import environ
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from sys import argv

apkpath = "~/Downloads/app-castrolZoomAlpha-release.apk"
aaptpath = "~/Library/Android/sdk/build-tools/28.0.1"
adbpath = "~/Library/Android/sdk/platform-tools"
pkgname = ''

"""
    Get list of android devices connected
"""


def get_devices():
    try:
        res = Popen(['adb', 'devices'], stdout=PIPE, stderr=STDOUT)
    except:
        print ('Either adb could not found in system PATH or adbpath variable not set where adb is located')
        exit(0)
    out = res.communicate()[0]
    ds = out.split('\n')
    ds = filter(lambda x: x != '' and 'devices' not in x,ds)
    ds = map(lambda x: x.strip('\tdevice'),ds)
    return res.returncode == 0, ds


"""
    Perform adb uninstall and report result as succees or fail
"""


def uninstall_apk(devid, devmodel, pkgname):
    cmd = 'adb -s {} uninstall {}'.format(devid,pkgname)
    res = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    r = (res.returncode == 0 and 'success' in out.lower())
    if r:
        print ('uninstall success on device {}'.format(devmodel))
    else:
        print ('uninstall failed on device {}'.format(devmodel))


"""
    Perform adb install and report result as succees or fail
"""


def install_apk(devid, devmodel, apkpath):
    cmd = 'adb -s {} install {}'.format(devid,apkpath)
    res = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    print ("Installing on {}".format(devmodel))
    out = res.communicate()[0]
    r = (res.returncode == 0 and 'success' in out.lower())
    if r:
        print ('Installation success on device {}'.format(devmodel))
    else:
        print ('Installation failed on device{}'.format(devmodel))
    return r


"""
    Find out the package name of the apk when package name is not provided but only the apk path
"""


def get_package_name(apkpath):
    cmd = 'aapt dump badging {} | grep package:\ name'.format(apkpath)
    res = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    l = out.split()
    for m in l:
        if m.startswith('name'):
            return True, m.split('\'')[1]
    print ('Either the file is not an apk or aapt is not set in system PATH or aaptpath variable not set where aapt '
           'is located')
    return False, ''


"""
    Check if a package is already installed on a connected device
"""


def is_installed(devid, pkgname):
    cmd = 'adb -s {} shell pm list packages | grep {}'.format(devid,pkgname)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    return pkgname in out


"""
    Get device model name from device id of the connected device
"""


def get_model(devid):
    cmd = 'adb -s {} shell getprop ro.product.model'.format(devid)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    return out.strip('\r').strip('\n').strip()


if __name__ == '__main__':
    argc = len(argv)
    ans = 'n'

    if argc != 3:
        print ('missing apk path and package name which are mandatory. pass empty arguments \'\' for both instead\n'
               'Supported modes are\n'
               'python apk_install.py \'\' \'\'\n'
               'python apk_install.py <apk path> \'\'\n'
               'python apk_install.py \'\' <package name>\n'
               'python apk_install.py <apk path> <package name>n')
        exit(0)

    if argv[1]:
        apkpath = str(argv[1])

    if argv[2]:
        pkgname = str(argv[2])

    """
        If the system PATH is not set in bash environment then use the aaptpath and adbpath to specify the
        path for adb and aapt executables
    """
    path = environ['PATH']
    environ['PATH'] = path+':'+aaptpath+':'+adbpath

    devmodel = {}
    installed = []

    r, ds = get_devices()
    if not len(ds):
        print ('no connected android devices found')
        exit(0)

    """
        Get the package name from apk file if not provided in command line
    """
    if pkgname.strip() == '' and apkpath.strip() != '':
        found, pkgname = get_package_name(apkpath)
        if not found:
            print ('no package found')
            exit(0)

    for d in ds:
        devmodel[d] = get_model(d)

    """
        Find out the devices on which the app is already installed
    """
    for d in ds:
        what = is_installed(d,pkgname)
        print ("Installed on {} : {}".format(devmodel[d],what))
        if what:
            installed.append(d)

    """
        Choose to uninstall the app on the devices if already installed
    """
    for who in installed:
        ans = raw_input('Do you wish to uninstall the app on {}? y/n \r\n'.format(devmodel[who]))
        if ans == 'y':
            uninstall_apk(who,devmodel[who],pkgname)
        else:
            ds.remove(who)

    """
        Install the apk on only those devices on which app is not installed
    """
    if not len(ds):
        print ('No devices to install the app on\n')
        exit(0)

    print ('Installing the apk on devices which don\'t have it installed or just uninstalled')
    threads = [Thread(target=install_apk, args=(d,devmodel[d],apkpath)) for d in ds]
    for t in threads:
        t.start()




