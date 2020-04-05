# apkSmartInstaller
This python file is to install and uninstall an apk on multiple android devices faster. This is currently compatible on mac OSX and Linux based OS.

python apk_install.py apk_file_path package_name

apk_file_path is optional, pass '' if not providing
package_name is optional, pass '' if not providing

apk_file_path and package_name when not '' they take precedene over the apkpath and pkgname variable configurstions within source file.

Dependency for the script to function
1. Compatible with mac OSX and Linux based machines. Tested on OSX.
2. Set the path to adb and aapt executables part of the android SDK's platform-tools and build-tools version. Either set the path to them in adbpath and aaptpath in source or set the paths in PATH environmnet variable.
3. If the package name is provided in command line or in variable pkgname in source then aapt dependecy is not present as we need not extract the package name from the apk file.




  
  

