from paver.easy import *
from paver.easy import path
import re
import json
import itertools
import platform

"""
Notes:

Java build tasks require maven to be on your path

C# tasks require Visual Studio and might need to be run using the
vcpaver.cmd script which sets up the VC environment variables. (You may
need to adjust the path to vcvarsall.bat in the vcpaver.cmd script)

ObjC tasks require clang.  To build the test application, you also need v8.
Version 3.9.24 is required. To install:
	
        First, go to the homebrew base directory
        $ cd $( brew --prefix )
        
        Then, check for homebrew versions for v8
        $ brew versions v8

        Find the git command for 3.9.24
        $ git checkout bb7fcab Library/Formula/v8.rb

        Then install v8
        $ brew install v8

For packaging sdks on windows, make sure 7zip is on your path.

Building docs requires markdown and django:
pip install markdown django

"""

PLATFORMS = {
	'ios': 'iOS',
	'mac': 'Mac',
	'android': 'Android',
	'win8': 'Windows 8',
	'winphone': 'Windows Phone',
}

DEBUG = False
CONFIGURATION = 'Release'

VERSION = json.load(open('current_version.json'))['version']


def _zip(archive_file, *args):
	if platform.system() == 'Windows':
		sh('7z a -tzip %s "%s"' % (archive_file, '", "'.join(args)))
	else:
		sh('zip -r %s "%s"' % (archive_file, '", "'.join(args)))


@task
def debug():
	global DEBUG, CONFIGURATION
	DEBUG = True
	CONFIGURATION = 'Debug'

# Java sdk for Android
def _make_java(path):
	with pushd(path):
		sh('mvn -pl Core clean install')
		sh('mvn -pl Tapstream clean package')
		sh('mvn -pl TapstreamTest clean package')

def _gen_java_whitelabel():
	path('java-whitelabel').rmtree()
	path.copytree(path('java'), path('java-whitelabel'))
	for d in ('Core', 'Tapstream', 'TapstreamTest'):
		path.move(path('java-whitelabel/%s/src/main/java/com/tapstream' % d), path('java-whitelabel/%s/src/main/java/com/conversiontracker' % d))
	path.move(path('java-whitelabel/Tapstream/src/test/java/com/tapstream'), path('java-whitelabel/Tapstream/src/test/java/com/conversiontracker'))
	path.move(path('java-whitelabel/Tapstream/src/main/java/com/conversiontracker/sdk/Tapstream.java'), path('java-whitelabel/Tapstream/src/main/java/com/conversiontracker/sdk/ConversionTracker.java'))

	package_name = re.compile(r'com\.tapstream\.sdk')
	class_name = re.compile(r'([\s("])Tapstream([\s(.])')
        def clean_file(file_path):
		with open(file_path, 'rb+') as f:
			data = f.read()
			data = package_name.sub('com.conversiontracker.sdk', data)
			data = class_name.sub(r'\1ConversionTracker\2', data)
			f.seek(0)
			f.write(data)
			f.truncate()
	for file_path in path('java-whitelabel').walkfiles('*.java'):
		clean_file(file_path)
	for file_path in path('java-whitelabel').walkfiles('pom.xml'):
		clean_file(file_path)

def _package_java():
	path('builds/android').rmtree()
	path('builds/android').makedirs()
	path.copy(path('./java/Tapstream/target/Tapstream-%s.jar' % VERSION), path('./builds/android/'))
	path.copy(path('./java/Tapstream/target/Tapstream-%s.jar' % VERSION), path('./examples/Android/Example/libs/'))
	path('builds/tapstream-%s-android.zip' % VERSION).remove()
	with pushd('builds/android'):
		_zip("../tapstream-%s-android.zip" % VERSION, 'Tapstream-%s.jar' % VERSION)

def _package_java_whitelabel():
	path('builds/android-whitelabel').rmtree()
	path('builds/android-whitelabel').makedirs()
	path.copy(path('./java-whitelabel/Tapstream/target/Tapstream-%s.jar' % VERSION), path('./builds/android-whitelabel/ConversionTracker.jar'))
	path('builds/tapstream-%s-android-whitelabel.zip' % VERSION).remove()
	with pushd('builds/android-whitelabel'):
		_zip("../tapstream-%s-android-whitelabel.zip" % VERSION, 'ConversionTracker.jar')
	path('java-whitelabel').rmtree()

@task
def make_java():
	_make_java('java')
	
@task
def test_java():
	sh('java -jar ./java/TapstreamTest/target/sdk-test-%s.jar tests.js' % VERSION)

@task
def package_java():
	_make_java('java')
	_gen_java_whitelabel()
	_make_java('java-whitelabel')
	_package_java()
	_package_java_whitelabel()



# C# sdk for Windows 8 and Windows Phone
@task
def make_cs():
	with pushd('cs'):
		sh('msbuild /m Tapstream.sln /t:Build /p:Configuration=%s /p:VisualStudioVersion=12.0' % CONFIGURATION)
		sh('msbuild /m TapstreamWinPhone.sln /t:Build /p:Configuration=%s' % CONFIGURATION)
		# Build win8 test code
		sh('msbuild /m TapstreamTest.sln /t:Build /p:Configuration=Debug;OutDir=bin/Debug/win8')
		# Build winphone test code
		sh('msbuild /m TapstreamTest.sln /t:Build /p:Configuration=Debug;OutDir=bin/Debug/winphone;DefineConstants="DEBUG;TRACE;TEST_WINPHONE"')

@task
def test_cs_win8():
	sh('"cs/TapstreamTest/bin/Debug/win8/TapstreamTest.exe" tests.js')

@task
def test_cs_winphone():
	sh('"cs/TapstreamTest/bin/Debug/winphone/TapstreamTest.exe" tests.js')

@task
def test_cs():
	test_cs_win8()
	test_cs_winphone()

@needs('make_cs')
@task
def package_cs():
	path('builds/win8').rmtree()
	path('builds/win8').makedirs()
	path.copy(path('./cs/Tapstream/bin/%s/TapstreamMetrics.winmd' % CONFIGURATION), path('./builds/win8/'))
	
	path('builds/winphone').rmtree()
	path('builds/winphone').makedirs()
	path.copy(path('./cs/TapstreamWinPhone/Bin/%s/TapstreamMetrics.dll' % CONFIGURATION), path('./builds/winphone/'))

	path('builds/tapstream-%s-win8.zip' % VERSION).remove()
	with pushd('builds/win8'):
		sh('7z a -tzip ../tapstream-%s-win8.zip TapstreamMetrics.winmd' % VERSION)

	path('builds/TapstreamSDK-winphone.zip').remove()
	with pushd('builds/winphone'):
		sh('7z a -tzip ../tapstream-%s-winphone.zip TapstreamMetrics.dll' % VERSION)





# ObjC sdk for Mac and iOS
def listify(series, prefix=''):
	return ' '.join(['%s%s' % (prefix, path(d).normpath().replace('\\', '/')) for d in series])

@task
def make_objc():
	with pushd('objc'):
		path('Tapstream/bin').mkdir()
		path('TapstreamTest/bin').mkdir()

		include_dirs = listify(['Core', '/usr/local/include/'], prefix='-I')

		core_sources = listify(path('Core').walkfiles('*.m'))
		tapstream_sources = ' '.join((
			core_sources,
			listify(path('Tapstream').walkfiles('*.m'))
		))
		tapstream_test_sources = ' '.join((
			core_sources,
			listify(path('TapstreamTest').walkfiles('*.m')),
			listify(path('TapstreamTest').walkfiles('*.mm'))
		))

		# Compile the non-test code as well to catch potential errors (even though this sdk will be distributed as source)

		# iOS With and without ARC
		clang = sh('echo xcrun -sdk iphoneos clang', capture=True).strip()
		sdk_root = sh('echo $(xcodebuild -version -sdk iphoneos Path)', capture=True).strip()
		sh('%s -isysroot %s -miphoneos-version-min=4.3 -arch armv7 -fno-objc-arc -shared %s %s -o ./TapstreamTest/bin/Tapstream.so -framework Foundation -framework UIKit -framework SafariServices -framework CoreGraphics' % (
			clang, sdk_root, include_dirs, tapstream_sources
		))
		sh('%s -isysroot %s -miphoneos-version-min=4.3 -arch armv7 -fobjc-arc -shared %s %s -o ./TapstreamTest/bin/Tapstream.so -framework Foundation -framework UIKit -framework SafariServices -framework CoreGraphics' % (
			clang, sdk_root, include_dirs, tapstream_sources
		))
		
		# Mac With and without ARC
		sh('clang -fno-objc-arc -shared %s %s -o ./TapstreamTest/bin/Tapstream.so -framework Foundation -framework AppKit -framework IOKit' % (
			include_dirs, tapstream_sources
		))
		sh('clang -fobjc-arc -shared %s %s -o ./TapstreamTest/bin/Tapstream.so -framework Foundation -framework AppKit -framework IOKit' % (
			include_dirs, tapstream_sources
		))

		# Compile test application for ios
		sh('clang++ -fobjc-arc %s %s -o ./TapstreamTest/bin/TapstreamTestIos -DTEST_IOS=1 -DTEST_PLATFORM=ios -lv8 -framework Foundation' % (
			include_dirs, tapstream_test_sources
		))
		# Compile test application for mac
		sh('clang++ -fobjc-arc %s %s -o ./TapstreamTest/bin/TapstreamTestMac -DTEST_PLATFORM=mac -lv8 -framework Foundation -framework IOKit' % (
			include_dirs, tapstream_test_sources
		))
		

@task
def test_objc_mac():
	sh('./objc/TapstreamTest/bin/TapstreamTestMac tests.js')

@task
def test_objc_ios():
	sh('./objc/TapstreamTest/bin/TapstreamTestIos tests.js')

@task
def test_objc():
	test_objc_mac()
	test_objc_ios()

@needs('make_objc')
@task
def package_objc():
	path('builds').mkdir()
	for sdk in ('mac', 'ios'):
		path('builds/%s' % sdk).rmtree()
		path('builds/%s/Tapstream' % sdk).makedirs()
		for file_type in ('.h', '.m'):
			sh('cp ./objc/Tapstream/*%s ./builds/%s/Tapstream/' % (file_type, sdk))
			sh('cp ./objc/Core/*%s ./builds/%s/Tapstream/' % (file_type, sdk))
		if sdk == 'ios':
			path('builds/%s/WordOfMouth' % sdk).makedirs()
			sh('cp -r ./objc/WordOfMouth/* ./builds/%s/WordOfMouth/' % sdk)
		path('builds/tapstream-%s-%s.zip' % (VERSION, sdk)).remove()
		with pushd('builds/%s' % sdk):
			folders = 'Tapstream ' + ('WordOfMouth' if sdk == 'ios' else '')
			sh('zip -r ../tapstream-%s-%s.zip %s' % (VERSION, sdk, folders))

		# Generate whitelabel
		path('builds/%s-whitelabel' % sdk).rmtree()
		path('builds/%s-whitelabel' % sdk).mkdir()
		sh('cp -r ./builds/%s/Tapstream ./builds/%s-whitelabel/' % (sdk, sdk))
		if sdk == 'ios':
			sh('cp -r ./builds/%s/WordOfMouth ./builds/%s-whitelabel/' % (sdk, sdk))
		with pushd('./builds/%s-whitelabel' % sdk):
			sh('mv Tapstream ConversionTracker')
			sh('mv ConversionTracker/TSTapstream.h ConversionTracker/ConversionTracker.h')
			sh('mv ConversionTracker/TSTapstream.m ConversionTracker/ConversionTracker.m')

			pattern = re.compile(r'(With|[\s\[("])(?:TS)?Tapstream([\s(.*:])')
			for file_path in itertools.chain(path('.').walkfiles('*.h'), path('.').walkfiles('*.m')):
				with open(file_path, 'rb+') as f:
					data = f.read()
					data = pattern.sub(r'\1ConversionTracker\2', data)
					f.seek(0)
					f.write(data)
					f.truncate()

		path('builds/tapstream-%s-%s-whitelabel.zip' % (VERSION, sdk)).remove()
		with pushd('builds/%s-whitelabel' % sdk):
			folders = 'ConversionTracker ' + ('WordOfMouth' if sdk == 'ios' else '')
			sh('zip -r ../tapstream-%s-%s-whitelabel.zip %s' % (VERSION, sdk, folders))


@needs('make_java', 'make_objc')
@task
def make_phonegap():
	path('builds/phonegap').rmtree()
	path('builds/phonegap').makedirs()
	sh('cp -r phonegap builds')
	sh('cp -r builds/ios/Tapstream builds/phonegap/src/ios')
	sh('cp builds/android/Tapstream-%s.jar builds/phonegap/src/android/Tapstream.jar' % VERSION)

	# Generate plugin xml elements that will copy each ios source file to the right place
	# Format these elements into the plugin file
	sources = path('builds/phonegap/src/ios/Tapstream').walkfiles('*.m')
	headers = path('builds/phonegap/src/ios/Tapstream').walkfiles('*.h')
	base = path('builds/phonegap')
	elements = ['        <source-file src="%s" />' % base.relpathto(s) for s in sources]
	elements += ['        <header-file src="%s" />' % base.relpathto(h) for h in headers]
	elements = '\n'.join(elements)

	with open('builds/phonegap/plugin.xml') as file:
		data = file.read()
	data = re.sub(r'{{\s*ios_sources\s*}}', elements, data)
	with open('builds/phonegap/plugin.xml', 'w') as file:
		file.write(data)

@needs('make_phonegap')
@task
def package_phonegap():
	path('builds/tapstream-%s-phonegap.zip' % VERSION).remove()
	with pushd('builds'):
		sh('cp -r phonegap tapstream-%s-phonegap' % VERSION)
		_zip('tapstream-%s-phonegap.zip' % VERSION, 'tapstream-%s-phonegap' % VERSION)
		sh('rm -rf tapstream-%s-phonegap' % VERSION)



@needs('make_java', 'make_objc')
@task
def make_titanium():
	path('builds/titanium').rmtree()
	path('builds/titanium').makedirs()
	sh('cp builds/android/Tapstream-%s.jar titanium/tapstream_android/lib/Tapstream.jar' % VERSION)
	path('titanium/tapstream_ios/Tapstream').rmtree()
	sh('cp -r builds/ios/Tapstream titanium/tapstream_ios')

	with pushd('titanium/tapstream_android'):
		sh('ant clean')
		sh('ant')
	sh('unzip titanium/tapstream_android/dist/com.tapstream.sdk-android-*.zip -d builds/titanium')

	with pushd('titanium/tapstream_ios'):
		sh('rm -f com.tapstream.sdk-iphone-*.zip')
		sh('python build.py')
	sh('unzip titanium/tapstream_ios/com.tapstream.sdk-iphone-*.zip -d builds/titanium')

@needs('make_titanium')
@task
def package_titanium():
	path('builds/tapstream-%s-titanium.zip' % VERSION).remove()
	with pushd('builds/titanium'):		
		_zip('../tapstream-%s-titanium.zip' % VERSION, 'modules')




def build_objc_static_lib(dest_path, additional_sources=[], addition_include_dirs=[]):
	# Compile Tapstream objc sources into static library
	sdk_root = sh('echo $(xcodebuild -version -sdk iphoneos Path)', capture=True).strip()
	simulator_sdk_root = sh('echo $(xcodebuild -version -sdk iphonesimulator Path)', capture=True).strip()

	include_dirs = listify(['objc/Core', 'objc/Tapstream', '/usr/local/include/']+addition_include_dirs, prefix='-I')
	core_sources = list(path('objc/Core').walkfiles('*.m'))
	inputs = core_sources + list(path('objc/Tapstream').walkfiles('*.m')) + [path(p) for p in additional_sources]

	sh('rm -f ./*.o')
	sh('xcrun -sdk iphoneos clang -isysroot %s -miphoneos-version-min=4.3 -arch armv7 -fno-objc-arc %s -c %s' % (
		sdk_root, include_dirs, listify(inputs)
	))
	sh('xcrun -sdk iphoneos ar rcu objc/TapstreamArm7.a ./*.o')
	sh('rm ./*.o')

	sh('xcrun -sdk iphoneos clang -isysroot %s -miphoneos-version-min=4.3 -arch armv7s -fno-objc-arc %s -c %s' % (
		sdk_root, include_dirs, listify(inputs)
	))
	sh('xcrun -sdk iphoneos ar rcu objc/TapstreamArm7s.a ./*.o')
	sh('rm ./*.o')

	sh('xcrun -sdk iphoneos clang -isysroot %s -miphoneos-version-min=4.3 -arch arm64 -fno-objc-arc %s -c %s' % (
		sdk_root, include_dirs, listify(inputs)
	))
	sh('xcrun -sdk iphoneos ar rcu objc/TapstreamArm64.a ./*.o')
	sh('rm ./*.o')

	sh('xcrun -sdk iphonesimulator clang -isysroot %s -miphoneos-version-min=4.3 -arch i386 -fobjc-abi-version=2 -fno-objc-arc %s -c %s' % (
		simulator_sdk_root, include_dirs, listify(inputs)
	))
	sh('xcrun -sdk iphonesimulator ar rcu objc/Tapstreami386.a ./*.o')
	sh('rm ./*.o')

	sh('xcrun -sdk iphonesimulator clang -isysroot %s -miphoneos-version-min=4.3 -arch x86_64 -fno-objc-arc %s -c %s' % (
		simulator_sdk_root, include_dirs, listify(inputs)
	))
	sh('xcrun -sdk iphonesimulator ar rcu objc/TapstreamX64.a ./*.o')
	sh('rm ./*.o')

	sh('xcrun -sdk iphoneos lipo -create objc/TapstreamArm7.a objc/TapstreamArm7s.a objc/TapstreamArm64.a objc/Tapstreami386.a objc/TapstreamX64.a -output %s' % dest_path)
	sh('rm objc/Tapstream*.a')


@task
def prepare_xamarin_lib():
	build_objc_static_lib('xamarin/Tapstream/TapstreamiOS/TapstreamiOS.a', ['xamarin/TapstreamObjcInterface.m'], ['objc/Core', 'objc/Tapstream'])

@needs('make_java')
@task
def make_xamarin():
	raise Exception("The Xamarin SDK must be built within Xamarin. So decrees the wizard of licensing!")


@task
def package_xamarin():
	sh('cp xamarin/Tapstream/TapstreamAndroid/bin/Release/TapstreamAndroid.dll builds/xamarin')
	sh('cp xamarin/Tapstream/TapstreamiOS/bin/Release/TapstreamiOS.dll builds/xamarin')
	path('builds/tapstream-%s-xamarin.zip' % VERSION).remove()
	with pushd('builds'):
		sh('cp -r xamarin tapstream-%s-xamarin' % VERSION)
		_zip('tapstream-%s-xamarin.zip' % VERSION, 'tapstream-%s-xamarin' % VERSION)
		sh('rm -rf tapstream-%s-xamarin' % VERSION)
	sh('echo "Make sure you built the project in Xamarin before running this"')




@needs('make_java')
@task
def make_unity():
	path('builds/unity').rmtree()
	path('builds/unity').makedirs()
	path('builds/unity/Plugins/iOS').makedirs()
	path('builds/unity/Plugins/Android').makedirs()
	with pushd('unity/java/'):
		sh('ant release')
	sh('cp unity/java/build/jar/Tapstream.jar builds/unity/Plugins/Android')
	sh('cp objc/Core/*.m builds/unity/Plugins/iOS')
	sh('cp objc/Core/*.h builds/unity/Plugins/iOS')
	sh('cp objc/Tapstream/*.m builds/unity/Plugins/iOS')
	sh('cp objc/Tapstream/*.h builds/unity/Plugins/iOS')
	sh('cp unity/TapstreamObjcInterface.m builds/unity/Plugins/iOS')
	sh('cp unity/Tapstream.cs builds/unity')
	# Update Example project
	sh('cp -r builds/unity/* examples/Unity/Assets/')

@needs('make_unity')
@task
def package_unity():
	path('builds/tapstream-%s-unity.zip' % VERSION).remove()
	with pushd('builds'):
		sh('cp -r unity tapstream-%s-unity' % VERSION)
		_zip('tapstream-%s-unity.zip' % VERSION, 'tapstream-%s-unity' % VERSION)
		sh('rm -rf tapstream-%s-unity' % VERSION)




