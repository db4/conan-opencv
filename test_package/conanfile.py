from conans import ConanFile, CMake, tools, RunEnvironment
import os

class OpenCVTestConan(ConanFile):
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            env_build = RunEnvironment(self)
            with tools.environment_append(env_build.vars):
                os.chdir("bin")
                if self.settings.os != "Windows":
                    # Work around OSX security restrictions
                    self.run("DYLD_LIBRARY_PATH=%s ./mytest outputfile.yml.gz" % os.environ['DYLD_LIBRARY_PATH'])
                else:
                    self.run("mytest outputfile.yml.gz")
