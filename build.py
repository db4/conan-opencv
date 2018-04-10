from conans import tools
from conan.packager import ConanMultiPackager
import platform

def main():
    """
    Main function.
    """

    builder = ConanMultiPackager(args="--build missing")
    builder.add_common_builds(shared_option_name="OpenCV:shared", pure_c=False)
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if platform.system() == "Windows" or tools.detected_architecture() == settings['arch']:
            # x86/x64 cross-compilation is supported on Windows only
            opts = dict(options)
            opts['OpenCV:with_ipp'] = True
            opts['OpenCV:with_tbb'] = True
            if platform.system() != "Windows" and opts['OpenCV:shared']:
                # jasper static lib is build without -fPIC
                opts['jasper:shared'] = True
            filtered_builds.append([settings, opts, env_vars, build_requires])
    builder.builds = filtered_builds
    builder.run()

if __name__ == "__main__":
    main()
