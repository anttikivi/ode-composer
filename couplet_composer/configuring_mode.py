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
This support module contains the functions for running the
configuration mode of the script.
"""

import os

from .support.environment import \
    get_build_root, get_dependencies_directory, get_tools_directory

from .util import shell


def create_build_root(source_root):
    """
    Checks if the directory for the local build files exists and
    creates it if it doesn't exist. Returns the path to the build
    root directory.

    source_root -- Path to the directory that is the root of the
    script run.
    """
    build_root = get_build_root(source_root=source_root)
    if not os.path.exists(build_root):
        shell.makedirs(path=build_root)
    return build_root


def create_tools_root(source_root, target):
    """
    Checks if the directory for the local tools exists and
    creates it if it doesn't exist. Returns the path to the tools
    directory.

    source_root -- Path to the directory that is the root of the
    script run.

    target -- The target system of the build represented by a
    Target.
    """
    tools_root = get_tools_directory(
        build_root=get_build_root(source_root=source_root),
        target=target
    )
    if not os.path.exists(tools_root):
        shell.makedirs(path=tools_root)
    return tools_root


def create_dependencies_root(source_root, target):
    """
    Checks if the directory for the dependencies exists and
    creates it if it doesn't exist. Returns the path to the
    dependecies directory.

    source_root -- Path to the directory that is the root of the
    script run.

    target -- The target system of the build represented by a
    Target.
    """
    dependencies_root = get_dependencies_directory(
        build_root=get_build_root(source_root=source_root),
        target=target
    )
    if not os.path.exists(dependencies_root):
        shell.makedirs(path=dependencies_root)
    return dependencies_root