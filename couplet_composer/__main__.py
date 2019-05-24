# ------------------------------------------------------------- #
#                       Couplet Composer
# ------------------------------------------------------------- #
#
# This source file is part of the Couplet Composer project which
# is part of the Obliging Ode and Unsung Anthem projects.
#
# Copyright (C) 2019 Antti Kivi
# All rights reserved
#
# ------------------------------------------------------------- #

"""The entry point of Couplet Composer."""

from __future__ import print_function

import json
import os
import re
import sys

from datetime import datetime

from absl import app, logging

from support import defaults

from support.defaults import SCRIPT_NAME

from support.presets import get_all_preset_names, get_preset_options

from support.variables import HOME, ODE_REPO_NAME, ODE_SOURCE_ROOT

from util import shell

from util.date import date_difference, to_date_string

from util.mapping import Mapping

from . import _clone

from .flags import FLAGS, register_flag_validators


def _is_preset_mode():
    return FLAGS.preset or FLAGS["show-presets"].value


def _run_preset():
    logging.debug(
        "Running %s in preset mode and thus the only flags that aren't "
        "ignored are: %s",
        SCRIPT_NAME,
        ", ".join([
            "dry-run",
            "print-debug",
            "clean",
            "jobs",
            "auth-token-file",
            "auth-token",
            "preset-files",
            "preset",
            "show-presets",
            "expand-build-script-invocation"
        ])
    )
    if not FLAGS["preset-files"].value:
        preset_file_names = [
            os.path.join(HOME, ".anthem-build-presets"),
            os.path.join(HOME, ".ode-build-presets"),
            os.path.join(
                ODE_SOURCE_ROOT,
                ODE_REPO_NAME,
                "util",
                "build-presets.ini"
            )
        ]
    else:
        preset_file_names = FLAGS["preset-files"].value

    logging.debug("The preset files are %s", ", ".join(preset_file_names))

    if FLAGS["show-presets"].value:
        logging.info("The available presets are:")
        for name in sorted(
            get_all_preset_names(preset_file_names),
            key=str.lower
        ):
            print(name)
        return

    if not FLAGS.preset:
        logging.fatal("Missing the '--preset' option")

    preset_args = get_preset_options(None, preset_file_names, FLAGS.preset)

    build_script_args = [sys.argv[0]]
    build_script_args += [sys.argv[1]]

    if FLAGS["dry-run"].value and FLAGS["dry-run"].present:
        build_script_args += ["--dry-run"]
    if FLAGS["print-debug"].value and FLAGS["print-debug"].present:
        build_script_args += ["--print-debug"]
    if FLAGS.clean and FLAGS["clean"].present:
        build_script_args += ["--clean"]
    if FLAGS.jobs and FLAGS["jobs"].present:
        build_script_args += ["--jobs", str(FLAGS.jobs)]
    if FLAGS["auth-token-file"].value and FLAGS["auth-token-file"].present:
        build_script_args += [
            "--auth-token-file", str(FLAGS["auth-token-file"].value)
        ]
    if FLAGS["auth-token"].value and FLAGS["auth-token"].present:
        build_script_args += ["--auth-token", str(FLAGS["auth-token"].value)]

    build_script_args += preset_args

    logging.info("Using preset '{}', which expands to \n\n{}\n".format(
        FLAGS.preset,
        shell.quote_command(build_script_args)
    ))
    logging.debug(
        "The script will have '{}' as the Python executable\n".format(
            sys.executable
        )
    )

    if FLAGS["expand-build-script-invocation"].value:
        logging.debug("The build script invocation is printed")
        return

    command_to_run = [sys.executable] + build_script_args

    shell.caffeinate(command_to_run)


def _run_bootstrap():
    logging.debug("%s was run in bootstrap mode", SCRIPT_NAME)
    _clone.download_dependencies()


def _run_build():
    logging.debug("%s was run in build mode", SCRIPT_NAME)


def main(argv):
    """Enters the program and runs it."""
    if FLAGS["print-debug"].value:
        logging.set_verbosity(logging.DEBUG)
    logging.debug("The non-flag arguments are %s", argv)
    if sys.version_info.major == 2:
        if sys.version_info.minor < 7:
            logging.fatal(
                "You're using Python %s, and the smallest supported version "
                "is %s",
                sys.version,
                "2.7"
            )
        else:
            logging.warning("You're using Python %s", sys.version)
            logging.warning(
                "You should really update to Python 3 to make the world a "
                "better place!"
            )
            # The end-of-life date of Python 2
            eol_date = datetime.strptime(
                "2020-01-01 00:00:00",
                "%Y-%m-%d %H:%M:%S"
            )
            now = datetime.now()
            logging.warning(
                "Also, the end of life of Python 2.7 is in %s, on 1 January, "
                "2020",
                to_date_string(date_difference(now, eol_date))
            )
    else:
        logging.debug("You're using Python %s", sys.version)
        logging.debug("You seem to have an excellent taste!")

    if not ODE_SOURCE_ROOT:
        logging.fatal(
            "Couldn't work out the source root directory (did you forget to "
            "set the '$ODE_SOURCE_ROOT' environment variable?)"
        )

    # The preset mode is the same for both bootstrap and build
    # mode so it's checked for first.
    if _is_preset_mode():
        _run_preset()
    else:
        if sys.argv[1] == "bootstrap" or sys.argv[1] == "boot":
            _run_bootstrap()
        elif sys.argv[1] == "build" or sys.argv[1] == "compose":
            _run_build()
        else:
            # Composer must have either bootstrap or build
            # subcommand. However, this need should always be
            # satisfied as Composer should only be run via the
            # scripts that come with Obliging Ode.
            logging.fatal(
                "%s wasn't in either bootstrap or build mode",
                SCRIPT_NAME
            )


def run():
    """
    Runs the script if Couplet Composer is invoked through
    'run.py'.
    """
    # The flag validators must be registered before running the
    # app as the app runs the validators and parses the flags.
    register_flag_validators()
    app.run(main)
    return 0


if __name__ == "__main__":
    sys.exit(run())
