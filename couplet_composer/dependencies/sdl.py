# ------------------------------------------------------------- #
#                       Couplet Composer
# ------------------------------------------------------------- #
#
# This source file is part of the Couplet Composer project which
# is part of the Obliging Ode and Unsung Anthem project.
#
# Copyright (c) 2019 Antti Kivi
# Licensed under the MIT License
#
# ------------------------------------------------------------- #

"""
This support module contains the functions related to the
building and finding Simple DirectMedia Layer.
"""

import os

from ..github import release

from ..support.environment import get_temporary_directory

from ..support.github_data import GitHubData

from ..support.platform_names import \
    get_darwin_system_name, get_linux_system_name, get_windows_system_name

from ..util.build_util import build_with_cmake

from ..util.cache import cached

from ..util import http, shell


################################################################
# DEPENDENCY DATA FUNCTIONS
################################################################


@cached
def should_install(dependencies_root, version, target, host_system):
    """
    Tells whether the build of the dependency should be skipped.

    dependencies_root -- The root directory of the dependencies
    for the current build target.

    version -- The full version number of the dependency.

    target -- The target system of the build represented by a
    Target.

    host_system -- The system this script is run on.
    """
    if host_system == get_windows_system_name():
        return not os.path.exists(os.path.join(
            dependencies_root,
            "lib",
            "SDL2.lib"
        ))
    else:
        return not os.path.exists(os.path.join(
            dependencies_root,
            "lib",
            "libSDL2.a"
        ))


def install_dependency(
    toolchain,
    cmake_generator,
    build_root,
    dependencies_root,
    version,
    target,
    host_system,
    github_user_agent,
    github_api_token,
    opengl_version,
    dry_run=None,
    print_debug=None
):
    """
    Installs the dependency by downloading and possibly building
    it. Returns the path to the built dependency.

    toolchain -- The toolchain object of the run.

    cmake_generator -- The name of the generator that CMake
    should use as the build system for which the build scripts
    are generated.

    build_root -- The path to the root directory that is used for
    all created files and directories.

    dependencies_root -- The root directory of the dependencies
    for the current build target.

    version -- The full version number of the dependency.

    target -- The target system of the build represented by a
    Target.

    host_system -- The system this script is run on.

    github_user_agent -- The user agent used when accessing the
    GitHub API.

    github_api_token -- The GitHub API token that is used to
    access the API.

    opengl_version -- The version of OpenGL that is used.

    dry_run -- Whether the commands are only printed instead of
    running them.

    print_debug -- Whether debug output should be printed.
    """
    temp_dir = get_temporary_directory(build_root=build_root)
    dependency_temp_dir = os.path.join(temp_dir, "sdl")

    shell.makedirs(temp_dir, dry_run=dry_run, echo=print_debug)
    shell.makedirs(dependency_temp_dir, dry_run=dry_run, echo=print_debug)

    url = ("https://www.libsdl.org/release/SDL2-devel-{version}-VC.zip"
           if host_system == get_windows_system_name()
           else "https://www.libsdl.org/release/SDL2-{version}.tar.gz").format(
        version=version
    )
    dest = os.path.join(
        dependency_temp_dir,
        "sdl.zip" if host_system == get_windows_system_name() else "sdl.tar.gz"
    )

    http.stream(
        url=url,
        destination=dest,
        host_system=host_system,
        dry_run=dry_run,
        print_debug=print_debug
    )
    shell.tar(dest, dependency_temp_dir, dry_run=dry_run, echo=print_debug)

    subdir = os.path.join(dependency_temp_dir, "SDL2-{}".format(version))

    if host_system == get_windows_system_name():
        if not os.path.isdir(os.path.join(dependencies_root, "include")):
            shell.makedirs(os.path.join(dependencies_root, "include"))
        include_dir = os.path.join(dependencies_root, "include", "SDL2")
        if os.path.isdir(include_dir):
            shell.rmtree(include_dir)
        shell.copytree(os.path.join(subdir, "include"), include_dir)
        if not os.path.isdir(os.path.join(dependencies_root, "lib")):
            shell.makedirs(os.path.join(dependencies_root, "lib"))
        for lib_file in os.listdir(os.path.join(
            dependencies_root,
            "lib"
        )):
            if "SDL" in lib_file:
                shell.rm(
                    os.path.join(dependencies_root, "lib", lib_file)
                )
        for lib_file in os.listdir(os.path.join(subdir, "lib", "x86")):
            shell.copy(
                os.path.join(subdir, "lib", "x86", lib_file),
                os.path.join(dependencies_root, "lib", lib_file)
            )
    else:
        build_with_cmake(
            toolchain=toolchain,
            cmake_generator=cmake_generator,
            source_directory=subdir,
            temporary_root=temp_dir,
            dependencies_root=dependencies_root,
            target=target,
            host_system=host_system,
            dry_run=dry_run,
            print_debug=print_debug
        )

    shell.rmtree(temp_dir, dry_run=dry_run, echo=print_debug)