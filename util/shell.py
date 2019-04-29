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

"""The support module containing shell helpers."""

from __future__ import print_function

import os
import pipes
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile

from contextlib import contextmanager

from absl import logging

from support import data


DEVNULL = getattr(subprocess, "DEVNULL", subprocess.PIPE)
DRY_RUN = False
ECHO = False


def _quote(arg):
    return pipes.quote(str(arg))


def quote_command(args):
    """Quotes a command for printing it."""
    return " ".join([_quote(a) for a in args])


def _coerce_dry_run(dry_run_override):
    if dry_run_override is None:
        return DRY_RUN
    else:
        return dry_run_override


def _coerce_echo(echo_override):
    if echo_override is None:
        return ECHO
    else:
        return echo_override


def _echo_command(dry_run, command, env=None, prompt="+ "):
    output = []
    if env is not None:
        output += ["env"] + [
            _quote("%s=%s" % (k, v)) for (k, v) in sorted(env.items())
        ]
    output += [_quote(arg) for arg in command]
    file = sys.stderr
    if dry_run:
        file = sys.stdout
    print(prompt + " ".join(output), file=file)
    file.flush()


def call(command, stderr=None, env=None, dry_run=None, echo=None):
    """Runs the given command."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, command, env=env)
    if dry_run:
        return
    _env = None
    if env is not None:
        _env = dict(os.environ)
        _env.update(env)
    try:
        subprocess.check_call(command, env=_env, stderr=stderr)
    except subprocess.CalledProcessError as e:
        logging.fatal(
            "Command ended with the status %d, stopping",
            e.returncode
        )
    except OSError as e:
        logging.fatal(
            "Couldn't run '%s': %s",
            quote_command(command),
            e.strerror
        )


def capture(
    command,
    stderr=None,
    env=None,
    dry_run=None,
    echo=None,
    optional=False,
    allow_non_zero_exit=False
):
    """Runs the given command and return its output."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, command, env=env)
    if dry_run:
        return
    _env = None
    if env is not None:
        _env = dict(os.environ)
        _env.update(env)
    try:
        out = subprocess.check_output(command, env=_env, stderr=stderr)
        # Coerce to 'str' hack. Not py3 'byte', not py2
        # 'unicode'.
        return str(out.decode())
    except subprocess.CalledProcessError as e:
        if allow_non_zero_exit:
            return e.output
        if optional:
            return None
        logging.fatal(
            "Command ended with the status %d, stopping",
            e.returncode
        )
    except OSError as e:
        if optional:
            return None
        logging.fatal(
            "Couldn't execute '%s': %s",
            quote_command(command),
            e.strerror
        )


@contextmanager
def pushd(path, dry_run=None, echo=None):
    """Pushes the directory to the top of the directory stack."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    old_dir = os.getcwd()
    if dry_run or echo:
        _echo_command(dry_run, ["pushd", path])
    if not dry_run:
        os.chdir(path)
    yield
    if dry_run or echo:
        _echo_command(dry_run, ["popd"])
    if not dry_run:
        os.chdir(old_dir)


def makedirs(path, dry_run=None, echo=None):
    """
    Creates the given directory and the in-between directories.
    """
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, ["mkdir", "-p", path])
    if dry_run:
        return
    if not os.path.isdir(path):
        os.makedirs(path)


def rmtree(path, dry_run=None, echo=None):
    """Removes a directory and its contents."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, ["rm", "-rf", path])
    if dry_run:
        return
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


def rm(file, dry_run=None, echo=None):
    """Removes a file."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, ["rm", "-f", file])
    if dry_run:
        return
    if os.path.islink(file):
        os.unlink(file)
    if os.path.exists(file):
        os.remove(file)


def copytree(src, dest, dry_run=None, echo=None):
    """Copies a directory and its contents."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, ["cp", "-r", src, dest])
    if dry_run:
        return
    # A workaround
    if os.path.isdir(dest):  # and data.build.ci:
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)  # , symlinks, ignore)
            else:
                shutil.copy2(s, d)
    else:
        shutil.copytree(src, dest)


def copy(src, dest, dry_run=None, echo=None):
    """Copies a file."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, ["cp", "-p", src, dest])
    if dry_run:
        return
    if os.path.islink(src):
        link = os.readlink(src)
        os.symlink(link, dest)
    else:
        shutil.copy2(src, dest)


def move(src, dest, dry_run=None, echo=None):
    """Moves a directory recursively."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        # TODO Check if the flag '-f' matches the behaviour.
        _echo_command(dry_run, ["mv", "-f", src, dest])
    if dry_run:
        return
    shutil.move(src, dest)


def listtree(path, dry_run=None, echo=None):
    """Prints a directory and its contents."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        _echo_command(dry_run, ["ls", "-R", path])
    if dry_run:
        return
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for name in filenames:
                print(os.path.join(os.path.relpath(dirpath, path), name))
    else:
        logging.warning("{} is not a directory!".format(path))


def tar(path, dest=None, dry_run=None, echo=None):
    """Extracts an archive."""
    dry_run = _coerce_dry_run(dry_run)
    echo = _coerce_echo(echo)
    if dry_run or echo:
        if dest:
            _echo_command(dry_run, ["tar", "-xf", path, "-C", dest])
        else:
            _echo_command(dry_run, ["tar", "-xf", path])
    if dry_run:
        return
    if path.endswith(".zip"):
        with zipfile.ZipFile(path, "r") as archive:
            if dest:
                archive.extractall(dest)
            else:
                archive.extractall()
    else:
        if path.endswith(".tar") or path.endswith(".tar.gz"):
            with tarfile.open(path) as archive:
                if dest:
                    archive.extractall(dest)
                else:
                    archive.extractall()
        else:
            if sys.version_info.major == 2:
                # TODO Use different command for Windows.
                with pushd(os.path.dirname(path)):
                    if dest:
                        call(
                            ["tar", "-xf", os.path.split(path)[1], "-C", dest])
                    else:
                        call(["tar", "-xf", os.path.split(path)[1]])
            else:
                with tarfile.open(path) as archive:
                    if dest:
                        archive.extractall(dest)
                    else:
                        archive.extractall()


def curl(url, dest, env=None, dry_run=None, echo=None):
    """Downloads a file."""
    call(
        ["curl", "-o", dest, "--create-dirs", url],
        env=env,
        dry_run=dry_run,
        echo=echo
    )


def caffeinate(command, env=None, dry_run=False, echo=None):
    """
    Runs a command during which system sleep is disabled. By
    default, this ignores the 'shell.dry_run' flag.
    """
    # Disable system sleep, if possible.
    if platform.system() == "Darwin":
        # Don't mutate the caller's copy of the arguments.
        command = ["caffeinate"] + list(command)
    call(command, env=env, dry_run=dry_run, echo=echo)
