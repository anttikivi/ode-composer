# Copyright (c) 2020 Antti Kivi
# Licensed under the MIT License

"""A module that contains the class for the objects that run the
composing run mode of the build script.
"""

from .runner import Runner


class ComposingRunner(Runner):
    """A class for creating callable objects that represent the
    composing mode runners of the build script.
    """

    def __call__(self) -> int:
        """Runs the run mode of this runner.

        Returns:
            An 'int' that is equal to the exit code of the run.
        """
        pass
