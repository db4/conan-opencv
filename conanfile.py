from conans import ConanFile, CMake, tools
import os
import json
import re
import stat

CONAN_REPO = "https://github.com/db4/conan-opencv"
OPENCV_REPO = "https://github.com/opencv/opencv.git -b {version}"

OPENCV_CONAN_PKG = {
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

# with_<pkg> options for conan-provided packages
OPTIONS_CONAN_PKG = [opt for opt in OPENCV_BUILD_OPTIONS if (opt[0].startswith(
    "with_")) and (opt[0].split("_", 1)[1] in OPENCV_CONAN_PKG)]

# Other options except options for conan-provided packages
OPTIONS_FILTERED = [opt for opt in OPENCV_BUILD_OPTIONS if (
    not opt[0].split("_", 1)[1] in OPENCV_CONAN_PKG)]


class OpenCVConan(ConanFile):
    # Description must be very short for conan.io
    description = "OpenCV: Open Source Computer Vision Library."
    name = "OpenCV"
    settings = "os", "compiler", "build_type", "arch"

    default_options = ("shared=False", "fPIC=True") + \
        tuple(["{0}={1}".format(opt[0], "True" if len(opt) < 3 else opt[2])
               for opt in OPTIONS_CONAN_PKG]) + \
        tuple(["{0}={1}".format(opt[0], "" if len(opt) < 3 else opt[2])
               for opt in OPTIONS_FILTERED])

    options = dict([(opt[0], [False, True]) for opt in OPTIONS_CONAN_PKG] +
                   [(opt[0], [False, True, ""]) for opt in OPTIONS_FILTERED])
    options["shared"] = [False, True]
    options["fPIC"] = [False, True]

    url = CONAN_REPO
    license = "http://http://opencv.org/license.html"
    generators = "cmake"
    short_paths = True
    no_copy_source = True
    build_requires = "cmake_config_tools/0.0.2@dbely/testing"

    def requirements(self):
        for lib in OPENCV_CONAN_PKG:
            with_lib = "with_"+lib
            if self.options.get_safe(with_lib) != False:
                pkg_info = OPENCV_CONAN_PKG[lib]
                pkg_ref = pkg_info[0]
                pkg_name = pkg_ref.split("/")[0]
                self.requires(pkg_ref)
                if len(pkg_info) > 1:
                    for (opt, value) in pkg_info[1]:
                        setattr(self.options[pkg_name], opt, value)
                if self.options.get_safe("shared") or self.options.get_safe("fPIC"):
                    if pkg_name == "jasper":
                        # jasper does not have fPIC option yet and is compiled without fPIC
                        self.options[pkg_name].shared = True
                    elif self.options[pkg_name].fPIC is not None:
                        self.options[pkg_name].fPIC = True

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        self.run("git clone " + OPENCV_REPO.format(version=self.version))
        tools.replace_in_file("opencv/CMakeLists.txt", "project(OpenCV CXX C)",
                              """project(OpenCV CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

# Don't call conan_basic_setup() as it affects TBB (-I<tbb_dir> is forced while OpenCV needs -isystem <tbb_dir>)
#conan_basic_setup()

conan_set_find_library_paths()
conan_set_libcxx()
""")

    def build(self):
        cmake = CMake(self)
        cmake_options = {}

        # - we can't use conan_global_flags() above because conan code is injected AFTER project()
        #   (overwise CMAKE_CXX_FLAGS are not set correctly), but it's too late for OpenCV to
        #   correctly detect cross-compilation
        # - we can't pass CMAKE_CXX_FLAGS via command line for Visual Studio as it clears various
        #   defines set by cmake like /DWIN32. Without them OpenCV build would fail
        #
        # So here is a workaround that's not universal (gcc/Win32 would fail), but works for
        # the most common cases (MSVC/Windows and gcc/Unix)

        if tools.cross_building(self.settings) and self.settings.compiler != "Visual Studio":
            cmake_options["CMAKE_C_FLAGS"] = cmake.definitions["CONAN_C_FLAGS"]
            cmake_options["CMAKE_CXX_FLAGS"] = cmake.definitions["CONAN_CXX_FLAGS"]

        for opt in OPENCV_BUILD_OPTIONS:
            opt_name = opt[0]
            if opt_name.startswith("build_opencv_"):
                words = opt_name.split("_")
                opt_opencv = "_".join([words[0].upper()]+words[1:])
            else:
                opt_opencv = opt_name.upper()
            if opt_name in self.options:
                value = getattr(self.options, opt_name)
                if value == "False" or value == "True":
                    cmake_options[opt_opencv] = value
            elif opt_name.startswith("build_"):
                pkg = opt_name.split("_", 1)[1]
                if pkg in OPENCV_CONAN_PKG:
                    cmake_options[opt_opencv] = False

        if self.options.with_tbb != "False" and self.settings.compiler != "Visual Studio":
            # work around OpenCV bug: TBB is incompatible with
            # precompiled headers in Linux build
            cmake_options["ENABLE_PRECOMPILED_HEADERS"] = False
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

        if "Visual Studio" in cmake.command_line:
            # Make CI logs manageable
            args = ["--", "/verbosity:minimal"]
        else:
            args = []
        cmake.build(target="install", args=args)

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
            # Work around OpenCV problems (exclude external libs like tbb)
            def check(lib):
                for pkg in OPENCV_CONAN_PKG:
                    if lib == pkg or lib == "-l" + pkg or \
                       lib == pkg + ".lib" or lib == pkg + ".a":
                        return False
                return True
            libs = [lib for lib in cpp_info["libs"] if check(lib)]
            # *.so.x.y.z -> *.so
            def convert(file):
                m = re.match(r'(.*\.so)\..*', file)
                if m is not None:
                    return m.group(1)
                else:
                    return file
            libs = [convert(lib) for lib in libs]
            # Exclude c++ lib that OpenCV adds explicitly)
            syslibs = [lib for lib in cpp_info["syslibs"] if lib != "stdc++"]
            cpp_info["libs"] = libs + syslibs
            cpp_info["bindirs"] = [os.path.join(
                os.path.dirname(cpp_info["libdirs"][0]), "bin")]
        cpp_info_json = os.path.join(self.package_folder, "cpp_info.json")
        tools.save(cpp_info_json, json.dumps(cpp_info))

    def package_info(self):
        cpp_info_json = os.path.join(self.package_folder, "cpp_info.json")
        cpp_info = json.loads(tools.load(cpp_info_json))

        includedirs = cpp_info["includedirs"]
        self.output.info("includedirs : " + ' '.join(includedirs))
        self.cpp_info.includedirs = includedirs

        libdirs = cpp_info["libdirs"]
        self.output.info("libdirs : " + ' '.join(libdirs))
        self.cpp_info.libdirs = libdirs

        libs = cpp_info["libs"]
        self.output.info("libs : " + ' '.join(libs))
        self.cpp_info.libs = libs

        bindirs = cpp_info["bindirs"]
        self.output.info("bindirs : " + ' '.join(bindirs))
        self.cpp_info.bindirs = bindirs
