# Copyright (c) 2019 Antti Kivi
# Licensed under the MIT License

"""
This support module reads the values from the project Couplet
Composer acts on.
"""

import json
import os

from ..util.cache import cached

from .file_paths import get_project_values_file_path

from .project_names import get_ode_repository_name


@cached
def _get_project_values_file(source_root, in_tree_build):
    """
    Gives the path to the file that contains the project values.

    source_root -- Path to the directory that is the root of the
    script run.

    in_tree_build -- Whether the build files are created in tree.
    """
    return os.path.join(source_root, get_project_values_file_path()) \
        if in_tree_build \
        else os.path.join(
            source_root,
            get_ode_repository_name(),
            get_project_values_file_path()
        )


@cached
def _get_project_values(source_root, in_tree_build):
    """
    Gives the project values.

    source_root -- Path to the directory that is the root of the
    script run.

    in_tree_build -- Whether the build files are created in tree.
    """
    try:
        with open(_get_project_values_file(
            source_root=source_root,
            in_tree_build=in_tree_build
        )) as f:
            return json.load(f)
    except Exception:
        return None


def get_ode_name():
    """Gives the name of Obliging Ode."""
    return "Obliging Ode"


def get_anthem_name():
    """Gives the name of Unsung Anthem."""
    return "Unsung Anthem"


@cached
def get_version(source_root, in_tree_build):
    """
    Gives the default version of the project.

    source_root -- Path to the directory that is the root of the
    script run.

    in_tree_build -- Whether the build files are created in tree.
    """
    project_values = _get_project_values(
        source_root=source_root,
        in_tree_build=in_tree_build
    )
    if project_values:
        return None if "version" not in project_values \
            else project_values["version"]
    else:
        return None


@cached
def get_ode_version(source_root, in_tree_build):
    """
    Gives the default version of Obliging Ode.

    source_root -- Path to the directory that is the root of the
    script run.

    in_tree_build -- Whether the build files are created in tree.
    """
    project_values = _get_project_values(
        source_root=source_root,
        in_tree_build=in_tree_build
    )
    if project_values:
        if "ode" not in project_values:
            return None
        if "version" not in project_values["ode"]:
            return None
        return project_values["ode"]["version"]
    else:
        return None


@cached
def get_anthem_version(source_root, in_tree_build):
    """
    Gives the default version of Unsung Anthem.

    source_root -- Path to the directory that is the root of the
    script run.

    in_tree_build -- Whether the build files are created in tree.
    """
    project_values = _get_project_values(
        source_root=source_root,
        in_tree_build=in_tree_build
    )
    if project_values:
        if "anthem" not in project_values:
            return None
        if "version" not in project_values["anthem"]:
            return None
        return project_values["anthem"]["version"]
    else:
        return None


def get_default_ode_window_name():
    """
    Gives the default name of the window of Obliging Ode.
    """
    return get_ode_name()


def get_default_anthem_window_name():
    """
    Gives the default name of the window of Unsung Anthem.
    """
    return get_anthem_name()


def get_ode_binaries_base_name():
    """
    Gives the default base name for the binaries of Obliging Ode.
    """
    return "ode"


def get_anthem_binaries_base_name():
    """
    Gives the default base name for the binaries of Unsung
    Anthem.
    """
    return "anthem"


@cached
def get_scripts_base_directory_name(coverage):
    """
    Gives the name of the base directory where the Lua scripts
    are copied to.

    coverage -- Whether or not code coverage is enabled.
    """
    return "scripts_lib" if coverage else "lib"
