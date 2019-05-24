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

"""This utility module handles the 'which' helpers."""

from __future__ import absolute_import

import sys

from . import cache_util, shell


@cache_util.cached
def which(cmd):
    """
    Return the path to an executable which would be run if the
    given cmd was called. If no cmd would be called, return None.

    Python 3.3+ provides this behaviour via the shutil.which()
    function; see:
    https://docs.python.org/3.3/library/shutil.html#shutil.which

    We provide our own implementation because shutil.which() has
    not been backported to Python 2.7, which we support.
    """
    if sys.version_info[0] >= 3:
        import shutil
        return shutil.which(cmd)
    out = shell.capture(
        ["which", cmd],
        dry_run=False,
        echo=False,
        optional=True
    )
    return out.rstrip() if out is not None else None


@cache_util.cached
def where(cmd):
    """
    Return the path to an executable which would be run if the
    given cmd was called. If no cmd would be called, return None.

    Python 3.3+ provides this behaviour via the shutil.which()
    function; see:
    https://docs.python.org/3.3/library/shutil.html#shutil.which

    We provide our own implementation because shutil.which() has
    not been backported to Python 2.7, which we support.
    """
    if sys.version_info[0] >= 3:
        import shutil
        return shutil.which(cmd)
    out = shell.capture(
        ["where.exe", cmd],
        dry_run=False,
        echo=False,
        optional=True
    )
    return out.rstrip() if out is not None else None
