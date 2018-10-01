from conan.packager import ConanMultiPackager
import os

available_versions = ["3.1.0", "3.4.0"]


def main():
    """
    Main function.
    """

    builder = ConanMultiPackager(build_policy="outdated")
    if "CONAN_REFERENCE" in os.environ:
        builder.add_common_builds(shared_option_name="OpenCV:shared", pure_c=False)
    else:
        for version in available_versions:
            builder.add_common_builds(shared_option_name="OpenCV:shared", pure_c=False, reference="OpenCV/%s@%s/%s" %
                                    (version, os.environ["CONAN_USERNAME"], os.environ["CONAN_CHANNEL"]))
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        with_ipp_tbb_list = [True] if options['OpenCV:shared'] else [True, False]
        for with_ipp_tbb in with_ipp_tbb_list:
            opts = dict(options)
            opts['OpenCV:with_ipp'] = with_ipp_tbb
            opts['OpenCV:with_tbb'] = with_ipp_tbb
            filtered_builds.append([settings, opts, env_vars, build_requires])
    builder.builds = filtered_builds
    builder.run()

if __name__ == "__main__":
    main()
