from conans import ConanFile, CMake, tools
import os
import json
import stat

CONAN_REPO = "https://github.com/db4/conan-opencv"
OPENCV_REPO = "https://github.com/opencv/opencv.git"
OPENCV_VERSION = "3.4.0"
OPENCV_BRANCH = "tags/" + OPENCV_VERSION

QT_PKG = None
TBB_PKG = "TBB/4.4.4@conan/stable"


class OpenCVConan(ConanFile):
    # Description must be very short for conan.io
    description = "OpenCV: Open Source Computer Vision Library."
    name = "OpenCV"
    version = OPENCV_VERSION
    settings = "os", "compiler", "build_type", "arch"
    default_options = "shared=False",\
        "with_gtk=False",\
        "with_qt=False",\
        "with_ipp=True",\
        "with_opengl=False",\
        "with_cuda=False",\
        "with_jpeg=True",\
        "build_jpeg=True",\
        "with_png=True",\
        "build_png=True",\
        "with_jasper=True",\
        "build_jasper=True",\
        "build_zlib=True",\
        "with_tiff=True",\
        "build_tiff=True",\
        "with_tbb=False",\
        "build_tbb=False",\
        "with_openexr=True",\
        "build_openexr=True",\
        "with_webp=True",\
        "build_webp=True",\
        "build_tests=False",\
        "build_perf_tests=False",\
        "build_opencv_apps=False",\
        "cpack_binary_nsis=False",\
        "build_opencv_calib3d=True",\
        "build_opencv_features2d=True",\
        "build_opencv_flann=True",\
        "build_opencv_highgui=True",\
        "build_opencv_imgcodecs=True",\
        "build_opencv_imgproc=True",\
        "build_opencv_ml=True",\
        "build_opencv_objdetect=True",\
        "build_opencv_photo=True",\
        "build_opencv_python2=True",\
        "build_opencv_python3=True",\
        "build_opencv_shape=True",\
        "build_opencv_stitching=True",\
        "build_opencv_superres=True",\
        "build_opencv_ts=True",\
        "build_opencv_video=True",\
        "build_opencv_videoio=True",\
        "build_opencv_videostab=True"
    options = {opt.split('=')[0]: [True, False] for opt in default_options}
    if TBB_PKG is None:
        options["with_tbb"] = [False]
    if QT_PKG is None:
        options["with_qt"] = [False]
    url = CONAN_REPO
    license = "http://http://opencv.org/license.html"
    generators = "cmake"
    short_paths = True
    requires = "cmake_config_tools/0.0.1@dbely/testing"

    def requirements(self):
        if self.options.with_qt:
            self.requires(QT_PKG)
        if self.options.with_tbb:
            self.requires(TBB_PKG)
            self.options["TBB"].shared = True

    def source(self):
        self.run("git clone " + OPENCV_REPO)
        self.run("cd opencv && git checkout " + OPENCV_BRANCH)

    def build(self):
        cmake = CMake(self)
        cmake_options = {}
        for opt, value in self.options.items():
            if opt == "shared":
                cmake_options["BUILD_SHARED_LIBS"] = value
            elif opt.startswith("build_opencv_"):
                words = opt.split("_")
                cmake_options["_".join([words[0].upper()]+words[1:])] = value
            else:
                cmake_options[opt.upper()] = value
        cmake_options["CMAKE_INSTALL_PREFIX"] = "install"
        if self.options.with_tbb:
            cmake_options["TBB_INCLUDE_DIR"] = self.deps_cpp_info["TBB"].includedirs[0]
        if self.settings.compiler == "Visual Studio":
            cmake_options["BUILD_WITH_STATIC_CRT"] = self.settings.compiler.runtime in [
                "MT", "MTd"]
        if self.settings.build_type == "Debug":
            # prevent pythonXX_d.lib link error
            cmake_options["BUILD_opencv_python2"] = False
            cmake_options["BUILD_opencv_python3"] = False
        cmake.configure(defs=cmake_options, source_folder="opencv")
        cmake.build(target="install")

    def package(self):
        self.copy(pattern="*", src="install", keep_path=True, symlinks=True)
        # LICENSE file is read-only so conan would raise an exception during packaging
        license_path = os.path.join(self.package_folder, "LICENSE")
        if os.path.exists(license_path):
            os.chmod(license_path, stat.S_IWRITE)

        opencv_install_dir = os.path.join(self.build_folder, "install")
        with tools.pythonpath(self):
            import cmake_config_tools  # pylint: disable=F0401
            if self.settings.os == "Windows":
                cpp_info = cmake_config_tools.cmake_find_package(
                    self, opencv_install_dir, "OpenCV")
            else:
                cpp_info = cmake_config_tools.cmake_find_package(
                    self, opencv_install_dir, "OpenCV", "share/OpenCV")
            # work around OpenCV problem (exclude external libs like tbb)
            cpp_info["libs"] = [lib for lib in cpp_info["libs"]
                                if not lib in OPENCV_3RDPARTY_PKG]
            cpp_info["bindirs"] = [os.path.join(
                os.path.dirname(cpp_info["libdirs"][0]), "bin")]
        cpp_info_json = os.path.join(self.package_folder, "cpp_info.json")
        tools.save(cpp_info_json, json.dumps(cpp_info))

    def package_info(self):
        cpp_info_json = os.path.join(self.package_folder, "cpp_info.json")
        cpp_info = json.loads(tools.load(cpp_info_json))

        self.cpp_info.includedirs = cpp_info["includedirs"]
        self.cpp_info.libdirs = cpp_info["libdirs"]
        self.cpp_info.libs = cpp_info["libs"]
        self.cpp_info.bindirs.extend(cpp_info["bindirs"])
