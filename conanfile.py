from conans import ConanFile, CMake, tools
import os
import json
import stat

CONAN_REPO = "https://github.com/db4/conan-opencv"
OPENCV_REPO = "https://github.com/opencv/opencv.git"
OPENCV_VERSION = "3.4.0"
OPENCV_BRANCH = "tags/" + OPENCV_VERSION

OPENCV_3RDPARTY_PKG = {
    # name, conan package, optional attribute list
    "jasper": ("jasper/2.0.14@conan/stable",),
    "jpeg": ("libjpeg/9b@bincrafters/stable",),
    "png": ("libpng/1.6.34@bincrafters/stable",),
    "tiff": ("libtiff/4.0.8@bincrafters/stable",),
    "zlib": ("zlib/1.2.11@conan/stable",),
    "webp": ("libwebp/0.6.1@bincrafters/stable",),

    "tbb": ("TBB/4.4.4@conan/stable", [("shared", True)]),
}

OPENCV_BUILD_OPTIONS = [
    # name, type, default value (optional)
    ("build_cuda_stubs", "bool"),
    ("build_docs", "bool", False),
    ("build_examples", "bool", False),
    ("build_ipp_iw", "bool"),
    ("build_itt", "bool"),
    ("build_jasper", "bool"),
    ("build_java", "bool"),
    ("build_jpeg", "bool"),
    ("build_openexr", "bool"),
    # ("build_package", "bool"),
    ("build_perf_tests", "bool", False),
    ("build_png", "bool"),
    ("build_protobuf", "bool"),
    # ("build_shared_libs", "bool"),
    ("build_tbb", "bool"),
    ("build_tests", "bool", False),
    ("build_tiff", "bool"),
    ("build_webp", "bool"),
    ("build_with_debug_info", "bool"),
    ("build_with_dynamic_ipp", "bool"),
    # ("build_with_static_crt", "bool"),
    ("build_zlib", "bool"),
    ("build_opencv_apps", "bool", False),
    ("build_opencv_calib3d", "bool"),
    ("build_opencv_core", "bool"),
    ("build_opencv_dnn", "bool"),
    ("build_opencv_features2d", "bool"),
    ("build_opencv_flann", "bool"),
    ("build_opencv_highgui", "bool"),
    ("build_opencv_imgcodecs", "bool"),
    ("build_opencv_imgproc", "bool"),
    ("build_opencv_js", "bool"),
    ("build_opencv_ml", "bool"),
    ("build_opencv_objdetect", "bool"),
    ("build_opencv_photo", "bool"),
    ("build_opencv_python2", "bool"),
    ("build_opencv_python3", "bool"),
    ("build_opencv_python_bindings_generator", "bool"),
    ("build_opencv_shape", "bool"),
    ("build_opencv_stitching", "bool"),
    ("build_opencv_superres", "bool"),
    ("build_opencv_ts", "bool"),
    ("build_opencv_video", "bool"),
    ("build_opencv_videoio", "bool"),
    ("build_opencv_videostab", "bool"),
    ("build_opencv_world", "bool"),
    ("enable_build_hardening", "bool"),
    ("enable_ccache", "bool"),
    ("enable_cxx11", "bool"),
    ("enable_impl_collection", "bool"),
    ("enable_instrumentation", "bool"),
    ("enable_lto", "bool"),
    # ("enable_noisy_warnings", "bool"),
    # ("enable_pic", "bool"),
    # ("enable_precompiled_headers", "bool"),
    # ("enable_pylint", "bool"),
    # ("enable_solution_folders", "bool"),
    # ("install_create_distrib", "bool"),
    ("install_c_examples", "bool", False),
    ("install_python_examples", "bool", False),
    # ("install_tests", "bool"),
    # ("opencv_config_file_include_dir", "string"),
    # ("opencv_download_path", "string"),
    ("opencv_enable_nonfree", "bool"),
    # ("opencv_extra_modules_path", "string"),
    ("opencv_force_python_libs", "bool"),
    ("opencv_warnings_are_errors", "bool"),
    ("with_1394", "bool"),
    ("with_clp", "bool"),
    ("with_cstripes", "bool"),
    ("with_cublas", "bool"),
    ("with_cuda", "bool"),
    ("with_cufft", "bool"),
    ("with_directx", "bool"),
    ("with_dshow", "bool"),
    ("with_eigen", "bool"),
    ("with_ffmpeg", "bool"),
    ("with_gdal", "bool"),
    ("with_gdcm", "bool"),
    ("with_gigeapi", "bool"),
    ("with_gstreamer", "bool"),
    ("with_gstreamer_0_10", "bool"),
    ("with_gtk", "bool"),
    ("with_gtk_2_x", "bool"),
    ("with_halide", "bool"),
    ("with_intelperc", "bool"),
    ("with_ipp", "bool"),
    ("with_itt", "bool"),
    ("with_jasper", "bool"),
    ("with_jpeg", "bool"),
    ("with_lapack", "bool"),
    ("with_matlab", "bool"),
    ("with_mfx", "bool"),
    ("with_msmf", "bool"),
    ("with_nvcuvid", "bool"),
    ("with_opencl", "bool"),
    ("with_openclamdblas", "bool"),
    ("with_openclamdfft", "bool"),
    ("with_opencl_svm", "bool"),
    ("with_openexr", "bool"),
    ("with_opengl", "bool"),
    ("with_openmp", "bool"),
    ("with_openni", "bool"),
    ("with_openni2", "bool"),
    ("with_openvx", "bool"),
    ("with_png", "bool"),
    ("with_pvapi", "bool"),
    ("with_qt", "bool"),
    ("with_tbb", "bool"),
    ("with_tiff", "bool"),
    ("with_vfw", "bool"),
    ("with_vtk", "bool"),
    ("with_webp", "bool"),
    ("with_win32ui", "bool"),
    ("with_ximea", "bool")
]

OPENCV_BUILD_OPTIONS_FILTERED = [opt for opt in OPENCV_BUILD_OPTIONS if (not opt[0].startswith(
    "build_")) or (not opt[0].split("_", 1)[1] in OPENCV_3RDPARTY_PKG)]


class OpenCVConan(ConanFile):
    # Description must be very short for conan.io
    description = "OpenCV: Open Source Computer Vision Library."
    name = "OpenCV"
    version = OPENCV_VERSION
    settings = "os", "compiler", "build_type", "arch"

    default_options = ("shared=False", "fPIC=True") + \
        tuple(["{0}={1}".format(opt[0], "" if len(opt) < 3 else opt[2])
               for opt in OPENCV_BUILD_OPTIONS_FILTERED])

    options = {opt[0]: [False, True, ""]
               for opt in OPENCV_BUILD_OPTIONS_FILTERED}
    options["shared"] = [False, True]
    options["fPIC"] = [False, True]

    url = CONAN_REPO
    license = "http://http://opencv.org/license.html"
    generators = "cmake"
    short_paths = True
    no_copy_source = True
    requires = "cmake_config_tools/0.0.1@dbely/testing"

    def requirements(self):
        for lib in OPENCV_3RDPARTY_PKG:
            with_lib = "with_"+lib
            if with_lib not in self.options or getattr(self.options, "with_"+lib) != False:
                pkg_info = OPENCV_3RDPARTY_PKG[lib]
                pkg_ref = pkg_info[0]
                pkg_name = pkg_ref.split("/")[0]
                self.requires(pkg_ref)
                if len(pkg_info) > 1:
                    for (opt, value) in pkg_info[1]:
                        setattr(self.options[pkg_name], opt, value)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        self.run("git clone " + OPENCV_REPO)
        self.run("cd opencv && git checkout " + OPENCV_BRANCH)
        tools.replace_in_file("opencv/CMakeLists.txt", "project(OpenCV CXX C)",
                              """project(OpenCV CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")

    def build(self):
        cmake = CMake(self)
        cmake_options = {}
        for opt in OPENCV_BUILD_OPTIONS:
            opt_name = opt[0]
            if opt_name.startswith("build_opencv_"):
                words = opt_name.split("_")
                opt_opencv = "_".join([words[0].upper()]+words[1:])
            else:
                opt_opencv = opt_name.upper()
            if opt_name in self.options:
                value = getattr(self.options, opt_name)
                if value != "":
                    cmake_options[opt_opencv] = value
            elif opt_name.startswith("build_"):
                pkg = opt_name.split("_", 1)[1]
                if pkg in OPENCV_3RDPARTY_PKG:
                    cmake_options[opt_opencv] = False

        # already set by CMake helper
        # cmake_options["BUILD_SHARED_LIBS"] = self.options.shared
        if "fPIC" in self.options:
            cmake_options["ENABLE_PIC"] = self.options.fPIC

        if self.settings.compiler == "Visual Studio":
            cmake_options["INSTALL_PDB"] = True
        if self.settings.compiler == "Visual Studio":
            cmake_options["BUILD_WITH_STATIC_CRT"] = self.settings.compiler.runtime in [
                "MT", "MTd"]
        if self.settings.build_type == "Debug":
            # prevent pythonXX_d.lib link error
            cmake_options["BUILD_opencv_python2"] = False
            cmake_options["BUILD_opencv_python3"] = False

        cmake_options["CMAKE_INSTALL_PREFIX"] = "install"
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
