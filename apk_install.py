from os import environ
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from sys import argv

filepath = "~/Downloads/app-castrolZoomAlpha-release.apk"
aaptpath = "~/Library/Android/sdk/build-tools/28.0.1"
adbpath = "~/Library/Android/sdk/platform-tools"
pname = 'com.abc.debug'

"""
    Get list of devices function
"""


def get_devices():
    try:
        res = Popen(['adb', 'devices'],stdout=PIPE,stderr=STDOUT)
    except:
        print ('Either adb could not found in system PATH or adbpath variable not set where adb is located')
        exit(0)
    out = res.communicate()[0]
    ds = out.split('\n')
    ds = filter(lambda x: x != '' and 'devices' not in x,ds)
    ds = map(lambda x: x.strip('\tdevice'),ds)
    return res.returncode == 0, ds


"""
    function to perform adb uninstall and report result as succees or fail
"""


def uninstall_apk(devid, devmodel, pkgname):
    cmd = 'adb -s {} uninstall {}'.format(devid,pkgname)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    r = (res.returncode == 0 and 'success' in out.lower())
    if r:
        print ('uninstall success on device {}'.format(devmodel))
    else:
        print ('uninstall failed on device {}'.format(devmodel))


"""
    function to perform adb install and report result as succees or fail
"""


def install_apk(devid, devmodel, apkpath):
    cmd = 'adb -s {} install {}'.format(devid,apkpath)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    print ("Installing on {}".format(devmodel))
    out = res.communicate()[0]
    r = (res.returncode == 0 and 'success' in out.lower())
    if r:
        print ('Installation success on device {}'.format(devmodel))
    else:
        print ('Installation failed on device{}'.format(devmodel))
    return r


def get_package_name(apkpath):
    cmd = 'maapt dump badging {} | grep package:\ name'.format(apkpath)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    l = out.split()
    for m in l:
        if m.startswith('name'):
            return True, m.split('\'')[1]
    print ('Either the file is not an apk or aapt is not set in system PATH or aaptpath variable not set where aapt is'
           'located')
    return False, ''


def is_installed(devid, pkgname):
    cmd = 'adb -s {} shell pm list packages | grep {}'.format(devid,pkgname)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    return pkgname in out


def get_model(devid):
    cmd = 'adb -s {} shell getprop ro.product.model'.format(devid)
    res = Popen(cmd,stdout=PIPE,stderr=STDOUT, shell=True)
    out = res.communicate()[0]
    return out.strip('\r').strip('\n').strip()


"""
    Deploy one device to each thread
"""

if __name__=='__main__':
    argc = len(argv)

    if argc !=3:
        print ('missing apk path and package name which are mandatory. pass empty arguments \'\' for both instead\n'
               'Supported modes are\n'
               'python apk_install.py \'\' \'\'\n'
               'python apk_install.py <apk path> \'\'\n'
               'python apk_install.py \'\' <package name>\n'
               'python apk_install.py <apk path> <package name>n')
        exit(0)

    if argv[1]:
        filepath = str(argv[1])

    if argv[2]:
        pname = str(argv[2])

    path = environ['PATH']
    environ['PATH'] = path+':'+aaptpath+':'+adbpath

    devmodel = {}
    installed = []

    r, ds = get_devices()
    if not len(ds):
        print ('no devices found')
        exit(0)

    if pname.strip() == '':
        found, pname = get_package_name(filepath)
        if not found:
            print ('no package found')
            exit(0)


    for d in ds:
        devmodel[d] = get_model(d)

    for d in ds:
        what = is_installed(d,pname)
        print ("Installed on {} : {}".format(devmodel[d],what))
        if what:
            installed.append(d)

    for who in installed:
        ans = raw_input('Do you wish to uninstall the app on {}? y/n \r\n'.format(devmodel[who]))
        if ans == 'y':
            uninstall_apk(who,devmodel[who],pname)
        else:
            ds.remove(who)

    threads = [Thread(target=install_apk, args=(d,devmodel[d],filepath)) for d in ds]
    for t in threads:
        t.start()




