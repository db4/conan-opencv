from conans import ConanFile, CMake, tools
import os
import re
import json
from io import StringIO

CONAN_REPO = "https://github.com/db4/conan-opencv"
OPENCV_REPO = "https://github.com/opencv/opencv.git"
OPENCV_VERSION = "3.4.0"
OPENCV_BRANCH = "tags/" + OPENCV_VERSION

QT_PKG = None
TBB_PKG = "TBB/4.4.4@memsharded/testing"

CMAKELISTS_TXT = r"""
cmake_minimum_required(VERSION 2.8.12)
# --- begin CMakeExpandImportedTargets.cmake ---

#.rst:
# CMakeExpandImportedTargets
# --------------------------
# Dmitry Bely <dmitry.bely@gmail.com>:
#   Import lib support, parse $<LINK_ONLY:(.*)> generator expressions, exclude duplicates
#
# ::
#
#  CMAKE_EXPAND_IMPORTED_TARGETS(<var> LIBRARIES lib1 lib2...libN
#                                [CONFIGURATION <config>])
#
# CMAKE_EXPAND_IMPORTED_TARGETS() takes a list of libraries and replaces
# all imported targets contained in this list with their actual file
# paths of the referenced libraries on disk, including the libraries
# from their link interfaces.  If a CONFIGURATION is given, it uses the
# respective configuration of the imported targets if it exists.  If no
# CONFIGURATION is given, it uses the first configuration from
# ${CMAKE_CONFIGURATION_TYPES} if set, otherwise ${CMAKE_BUILD_TYPE}.
# This macro is used by all Check*.cmake files which use try_compile()
# or try_run() and support CMAKE_REQUIRED_LIBRARIES , so that these
# checks support imported targets in CMAKE_REQUIRED_LIBRARIES:
#
# ::
#
#     cmake_expand_imported_targets(expandedLibs
#       LIBRARIES ${CMAKE_REQUIRED_LIBRARIES}
#       CONFIGURATION "${CMAKE_TRY_COMPILE_CONFIGURATION}" )


#=============================================================================
# Copyright 2012 Kitware, Inc.
# Copyright 2009-2012 Alexander Neundorf <neundorf@kde.org>
#
# Distributed under the OSI-approved BSD License (the "License");
# see accompanying file Copyright.txt for details.
#
# This software is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the License for more information.
#=============================================================================
# (To distribute this file outside of CMake, substitute the full
#  License text for the above reference.)

include(CMakeParseArguments)

function(CMAKE_EXPAND_IMPORTED_TARGETS _RESULT )

   set(options )
   set(oneValueArgs CONFIGURATION )
   set(multiValueArgs LIBRARIES )

   cmake_parse_arguments(CEIT "${options}" "${oneValueArgs}" "${multiValueArgs}"  ${ARGN})

   if(CEIT_UNPARSED_ARGUMENTS)
      message(FATAL_ERROR "Unknown keywords given to CMAKE_EXPAND_IMPORTED_TARGETS(): \"${CEIT_UNPARSED_ARGUMENTS}\"")
   endif()

   if(NOT CEIT_CONFIGURATION)
      if(CMAKE_CONFIGURATION_TYPES)
         list(GET CMAKE_CONFIGURATION_TYPES 0 CEIT_CONFIGURATION)
      else()
         set(CEIT_CONFIGURATION ${CMAKE_BUILD_TYPE})
      endif()
      string(TOUPPER ${CEIT_CONFIGURATION} CEIT_CONFIGURATION)
   endif()

   # handle imported library targets

   set(_CCSR_REQ_LIBS ${CEIT_LIBRARIES})

   set(_CHECK_FOR_IMPORTED_TARGETS TRUE)
   set(_CCSR_LOOP_COUNTER 0)
   while(_CHECK_FOR_IMPORTED_TARGETS)
      math(EXPR _CCSR_LOOP_COUNTER "${_CCSR_LOOP_COUNTER} + 1 ")
      set(_CCSR_NEW_REQ_LIBS )
      set(_CHECK_FOR_IMPORTED_TARGETS FALSE)
      foreach(_CURRENT_LIB ${_CCSR_REQ_LIBS})
         if(TARGET "${_CURRENT_LIB}")
            get_target_property(_imported "${_CURRENT_LIB}" IMPORTED)
         else()
            set(_imported "")
         endif()
         if (_imported)
#            message(STATUS "Detected imported target ${_CURRENT_LIB}")
            # Ok, so this is an imported target.
            # First we get the imported configurations.
            # Then we get the location of the actual library on disk of the first configuration.
            # then we'll get its link interface libraries property,
            # iterate through it and replace all imported targets we find there
            # with there actual location.

            # guard against infinite loop: abort after 100 iterations ( 100 is arbitrary chosen)
            if ("${_CCSR_LOOP_COUNTER}" LESS 100)
               set(_CHECK_FOR_IMPORTED_TARGETS TRUE)
#                else ()
#                   message(STATUS "********* aborting loop, counter : ${_CCSR_LOOP_COUNTER}")
            endif ()

            get_target_property(_importedConfigs "${_CURRENT_LIB}" IMPORTED_CONFIGURATIONS)
            if (_importedConfigs)
               # if one of the imported configurations equals ${CMAKE_TRY_COMPILE_CONFIGURATION},
               # use it, otherwise skip:
               list(FIND _importedConfigs "${CEIT_CONFIGURATION}" _configIndexToUse)
               if(NOT "${_configIndexToUse}" EQUAL -1)
                  list(GET _importedConfigs ${_configIndexToUse} _importedConfigToUse)

                  get_target_property(_importedLocation "${_CURRENT_LIB}" IMPORTED_IMPLIB_${_importedConfigToUse})
                  if(NOT _importedLocation)
                     get_target_property(_importedLocation "${_CURRENT_LIB}" IMPORTED_LOCATION_${_importedConfigToUse})
                  endif()
                  list(APPEND _CCSR_NEW_REQ_LIBS  "${_importedLocation}")
#                  message(STATUS "Appending lib ${_CURRENT_LIB} as ${_importedLocation}")

                  get_target_property(_linkInterfaceLibs "${_CURRENT_LIB}" IMPORTED_LINK_INTERFACE_LIBRARIES_${_importedConfigToUse} )
                  if(NOT _linkInterfaceLibs)
                     get_target_property(_linkInterfaceLibs "${_CURRENT_LIB}" INTERFACE_LINK_LIBRARIES)
                  endif()
                  if(_linkInterfaceLibs)
                     foreach(_currentLinkInterfaceLib ${_linkInterfaceLibs})
                        if("${_currentLinkInterfaceLib}" MATCHES "\\\$<LINK_ONLY:(.*)>")
                           set(_currentLinkInterfaceLib ${CMAKE_MATCH_1})
                        endif()
#                        message(STATUS "Appending link interface lib ${_currentLinkInterfaceLib}")
                        if(_currentLinkInterfaceLib)
                           list(APPEND _CCSR_NEW_REQ_LIBS "${_currentLinkInterfaceLib}" )
                        endif()
                     endforeach()
                  endif()
               endif()
            else()
               get_target_property(_importedLocation "${_CURRENT_LIB}" IMPORTED_IMPLIB)
               if(NOT _importedLocation)
                  get_target_property(_importedLocation "${_CURRENT_LIB}" IMPORTED_LOCATION)
               endif()
               list(APPEND _CCSR_NEW_REQ_LIBS  "${_importedLocation}")
#               message(STATUS "Appending lib ${_CURRENT_LIB} as ${_importedLocation}")

               get_target_property(_linkInterfaceLibs "${_CURRENT_LIB}" IMPORTED_LINK_INTERFACE_LIBRARIES)
               if(NOT _linkInterfaceLibs)
                  get_target_property(_linkInterfaceLibs "${_CURRENT_LIB}" INTERFACE_LINK_LIBRARIES)
               endif()
               if(_linkInterfaceLibs)
                  foreach(_currentLinkInterfaceLib ${_linkInterfaceLibs})
                     if("${_currentLinkInterfaceLib}" MATCHES "\\\$<LINK_ONLY:(.*)>")
                        set(_currentLinkInterfaceLib ${CMAKE_MATCH_1})
                     endif()
#                     message(STATUS "Appending link interface lib ${_currentLinkInterfaceLib}")
                     if(_currentLinkInterfaceLib)
                        list(APPEND _CCSR_NEW_REQ_LIBS "${_currentLinkInterfaceLib}" )
                     endif()
                  endforeach()
               endif()
            endif()
         else()
            # "Normal" libraries are just used as they are.
            list(APPEND _CCSR_NEW_REQ_LIBS "${_CURRENT_LIB}" )
#            message(STATUS "Appending lib directly: ${_CURRENT_LIB}")
         endif()
      endforeach()

      set(_CCSR_REQ_LIBS ${_CCSR_NEW_REQ_LIBS} )
   endwhile()

   # Finally we iterate once more over all libraries. This loop only removes
   # all remaining imported target names (there shouldn't be any left anyway).
   set(_CCSR_NEW_REQ_LIBS )
   foreach(_CURRENT_LIB ${_CCSR_REQ_LIBS})
      if(TARGET "${_CURRENT_LIB}")
        get_target_property(_importedConfigs "${_CURRENT_LIB}" IMPORTED_CONFIGURATIONS)
      else()
        set(_importedConfigs "")
      endif()
      if (NOT _importedConfigs)
         list(APPEND _CCSR_NEW_REQ_LIBS "${_CURRENT_LIB}" )
#         message(STATUS "final: appending ${_CURRENT_LIB}")
      else ()
#             message(STATUS "final: skipping ${_CURRENT_LIB}")
      endif ()
   endforeach()
   if(_CCSR_NEW_REQ_LIBS)
      list(REMOVE_DUPLICATES _CCSR_NEW_REQ_LIBS)
   endif()
#   message(STATUS "setting -${_RESULT}- to -${_CCSR_NEW_REQ_LIBS}-")
   set(${_RESULT} "${_CCSR_NEW_REQ_LIBS}" PARENT_SCOPE)

endfunction()
# --- end CMakeExpandImportedTargets.cmake ---

if (BUILD_SHARED_LIBS)
    set(OpenCV_STATIC OFF)
else()
    set(OpenCV_STATIC ON)
endif()
include(${CMAKE_CURRENT_LIST_DIR}/../install/OpenCVConfig.cmake)
cmake_expand_imported_targets(OpenCV_LIBS_DEBUG_EXPANDED LIBRARIES ${OpenCV_LIBS} CONFIGURATION DEBUG)
cmake_expand_imported_targets(OpenCV_LIBS_RELEASE_EXPANDED LIBRARIES ${OpenCV_LIBS} CONFIGURATION RELEASE)
set(OpenCV_LIBS ${OpenCV_LIBS_DEBUG_EXPANDED} ${OpenCV_LIBS_RELEASE_EXPANDED})
message(STATUS __BEGIN__)
get_cmake_property(_variableNames VARIABLES)
foreach (_variableName ${_variableNames})
    string(REGEX MATCH "^OpenCV" _ovar ${_variableName})
    if(NOT _ovar STREQUAL "")
        message(STATUS "${_variableName}=${${_variableName}}")
    endif()
endforeach()
message(STATUS __END__)
"""


def _parse_cmake_vars(output):
    res = {}
    start_reached = False
    for line in output.splitlines():
        if not start_reached:
            if "__BEGIN__" in line:
                start_reached = True
            continue
        elif "__END__" in line:
            break
        mobj = re.match(r"-- (\w+)=(.*)", line)
        if mobj:
            name = mobj.group(1)
            value = mobj.group(2)
            if ";" in value:
                value = value.split(";")
            res[name] = value
    return res


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
        # LICENSE file is read-only so conan would raise an exception during packaging
        self.copy(pattern="*", src="install",
                  excludes="LICENSE", keep_path=True)
        # The following is needed to import binaries to consumer projects.
        # They tend to expect "bin" location for binaries
        self.copy(pattern="*.dll", dst="bin", src="install", keep_path=False)
        self.copy(pattern="*.exe", dst="bin", src="install", keep_path=False)

        detect_dir = os.path.join(self.build_folder, "_detect_opencv")
        opencv_install_dir = os.path.join(self.build_folder, "install")
        cmakelists_txt_path = os.path.join(detect_dir, "CMakeLists.txt")
        tools.save(cmakelists_txt_path, CMAKELISTS_TXT)

        cmake = CMake(self)
        cmd = "cmake . " + cmake.command_line
        output = StringIO()
        try:
            self.run(cmd, cwd=detect_dir, output=output)
        except:
            print(output.getvalue())
            raise
        cmake_vars = _parse_cmake_vars(output.getvalue())
        #for (key, value) in cmake_vars.items():
        #    print("{0}={1}".format(key, value))
        if cmake_vars["OpenCV_FOUND"] != "TRUE":
            print(output.getvalue())
            raise Exception("Failed to find OpenCV")
        output.close()

        cpp_info = {}
        cpp_info["includedirs"] = [os.path.relpath(path, opencv_install_dir)
                                   for path in cmake_vars["OpenCV_INCLUDE_DIRS"]]
        cpp_info["libs"] = [os.path.basename(lib)
                            for lib in cmake_vars["OpenCV_LIBS"]]
        libdirs = []
        for libpath in cmake_vars["OpenCV_LIBS"]:
            try:
                libdirs.append(os.path.relpath(os.path.dirname(libpath), opencv_install_dir))
            except:
                # system libs like ws2_32 do not have path component
                pass
        cpp_info["libdirs"] = list(set(libdirs))
        cpp_info["bindirs"] = [os.path.join(os.path.dirname(libdirs[0]), "bin")]

        cpp_info_json = os.path.join(self.package_folder, "cpp_info.json")
        tools.save(cpp_info_json, json.dumps(cpp_info))

    def package_info(self):
        cpp_info_json = os.path.join(self.package_folder, "cpp_info.json")
        cpp_info = json.loads(tools.load(cpp_info_json))

        self.cpp_info.includedirs = cpp_info["includedirs"]
        self.cpp_info.libdirs = cpp_info["libdirs"]
        self.cpp_info.libs = cpp_info["libs"]
        self.cpp_info.bindirs.extend(cpp_info["bindirs"])
