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
This support module contains the functions for running the preset
mode of the script.
"""

from __future__ import print_function

import logging
import sys

from .support.presets import get_all_preset_names, get_preset_options

from .support.mode_names import \
    get_composing_mode_name, get_configuring_mode_name

from .util import shell


def show_presets(file_names):
    """
    Shows the available presets and returns the end code of this
    execution. This function isn't pure as it prints out the
    names of the presets.

    file_names -- The preset file names from which the preset
    names are read.
    """
    logging.info("The available presets are:")
    for name in sorted(get_all_preset_names(file_names), key=str.lower):
        print(name)
    return 0


def _compose_preset_option_list(preset_options):
    """
    Composes the given dictionary of parsed preset options to a
    list of strings.

    preset_options -- The dictionary containing the parsed preset
    options.
    """
    argument_list = []
    for key, value in preset_options.items():
        if value:
            argument_list.append("--{}={}".format(key, value))
        else:
            argument_list.append("--{}".format(key))
    return argument_list


def compose_preset_call(arguments, file_names):
    """
    Creates the call used to call the script in preset mode. This
    function isn't pure.

    arguments -- The parsed command line arguments of the script.

    file_names -- The preset file names from which the preset
    names are read.
    """

    preset_options, preset_options_after_end = get_preset_options(
        preset_file_names=file_names,
        preset_name=arguments.preset,
        substitutions=None
    )

    build_call = [sys.argv[0]]

    if arguments.preset_run_mode == get_configuring_mode_name():
        build_call.append(get_configuring_mode_name())
    elif arguments.preset_run_mode == get_composing_mode_name():
        build_call.append(get_composing_mode_name())

    if arguments.dry_run:
        build_call.append("--dry-run")
    # TODO Contemplate whether this should be able to be set from
    # preset mode
    if arguments.jobs:
        build_call.extend(["--jobs", str(arguments.jobs)])
    if arguments.clean:
        build_call.append("--clean")
    if arguments.print_debug:
        build_call.append("--print-debug")

    preset_arguments = _compose_preset_option_list(preset_options)
    preset_arguments_after_end = _compose_preset_option_list(
        preset_options_after_end
    )

    build_call.extend(preset_arguments)
    build_call.append("--")
    build_call.extend(preset_arguments_after_end)

    return build_call


def print_script_invocation(build_call, preset_name, executable):
    """
    Prints the script invocation that is expanded from a preset.
    This function isn't pure as its purpose is to print the
    invocation.

    build_call -- The script call that is expanded from the
    preset.

    preset_name -- Name of the preset that was used.

    executable -- The Python executable that will be used.
    """
    logging.info(
        "Using preset '%s', which expands to \n\n%s\n",
        preset_name,
        shell.quote_command(build_call)
    )

    logging.debug(
        "The script will use '%s' as the Python executable\n",
        executable
    )