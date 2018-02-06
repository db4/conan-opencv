from conan.packager import ConanMultiPackager

def main():
    """
    Main function.
    """

    builder = ConanMultiPackager(username="dbely", channel="testing")
    builder.visual_runtimes = ["MD", "MDd"]
    builder.visual_versions = ["15"]
    builder.arch = ['x86_64']
    builder.add_common_builds()
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        opts = dict(options)
        for shared in [True, False]:
            opts1 = dict(opts)
            opts1['OpenCV:shared'] = shared
            for ipp_tbb in [True, False]:
                opts2 = dict(opts1)
                opts2['OpenCV:with_ipp'] = ipp_tbb
                opts2['OpenCV:with_tbb'] = ipp_tbb
                filtered_builds.append([settings, opts2, env_vars, build_requires])
    builder.builds = filtered_builds
    builder.run()

if __name__ == "__main__":
    main()
