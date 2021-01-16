# Copyright (c) 2020 Antti Kivi
# Licensed under the MIT License

"""A module that contains the base class for the objects that
represent the dependencies of the project that this build script
acts on. These dependencies need to be built into binaries for
linking.
"""

import os

from typing import Any

from .support.cmake_generator import CMakeGenerator

from .support.system import System

from .util import shell

from .build_directory import BuildDirectory

from .dependency import Dependency

from .invocation import Invocation


class BinaryDependency(Dependency):
    """A class for creating objects that represent the
    dependencies of the project that this build script acts on.
    These dependencies need to be built into binaries for
    linking.

    Attributes:
        cmake_options (dict): The optional extra CMake options
            from the project's information file for this
            dependency.
    """

    def __init__(
        self,
        key: str,
        name: str,
        version: str,
        commit: str,
        files: Any,
        test_only: bool,
        benchmark_only: bool,
        asset_name: str,
        repository: str,
        cmake_options: dict
    ) -> None:
        """Initializes the dependency object.

        Args:
            key (str): The simple identifier of this dependency.
            name (str): The full name of this dependency.
            version (str): The required version of the
                dependency.
            commit (str): The required commit of the dependency.
            files (str | list | dict): The file or files that are
                used to check and copy the files of this
                dependency.
            test_only (bool): Whether or not the dependency is
                needed only when building the tests.
            benchmark_only (bool): Whether or not the dependency
                is needed only when building the benchmarkings.
            asset_name (str): The name of the asset that will be
                downloaded from GitHub by default.
            repository (str): The GitHub repository of this
                dependency.
            cmake_options (dict): The optional extra CMake
                options from the project's information file for
                this dependency.
        """
        super().__init__(
            key=key,
            name=name,
            version=version,
            commit=commit,
            files=files,
            test_only=test_only,
            benchmark_only=benchmark_only,
            asset_name=asset_name,
            repository=repository
        )
        self.cmake_options = cmake_options

    def _build(
        self,
        source_path: str,
        invocation: Invocation,
        build_dir: BuildDirectory
    ) -> None:
        """Builds the dependency from the sources.

        Args:
            source_path (str): The path to the source directory
                of the dependency.
            invocation (Invocation): The current invocation.
            build_dir (BuildDirectory): The build directory
                object that is the main build directory of the
                build script invocation.
        """
        cmake_call = [
            invocation.runner.toolchain.cmake,
            source_path,
            "-DCMAKE_BUILD_TYPE={}".format(invocation.build_variant.value),
            "-DCMAKE_INSTALL_PREFIX={}".format(build_dir.dependencies)
        ]

        if invocation.platform is System.windows:
            pass  # TODO Set the compiler on Windows.

        if invocation.cmake_generator is CMakeGenerator.ninja:
            cmake_call.extend([
                "-DCMAKE_MAKE_PROGRAM={}".format(
                    invocation.runner.toolchain.ninja
                )
            ])

        cmake_call.extend(["-G", invocation.cmake_generator.value])

        if self.cmake_options:
            for k, v in self.cmake_options.items():
                if isinstance(v, bool):
                    cmake_call.extend(
                        ["-D{}={}".format(k, ("ON" if v else "OFF"))]
                    )
                else:
                    cmake_call.extend(["-D{}={}".format(k, v)])

        # TODO Add the C and C++ compilers to the environment
        cmake_env = None

        build_directory = os.path.join(build_dir.temporary, "build")

        if not os.path.isdir(build_directory):
            shell.makedirs(
                build_directory,
                dry_run=invocation.args.dry_run,
                echo=invocation.args.verbose
            )

        with shell.pushd(
            build_directory,
            dry_run=invocation.args.dry_run,
            echo=invocation.args.verbose
        ):
            shell.call(
                cmake_call,
                env=cmake_env,
                dry_run=invocation.args.dry_run,
                echo=invocation.args.verbose
            )
            # TODO Take into account all of the different build
            # systems.
            shell.call(
                [invocation.runner.toolchain.ninja],
                dry_run=invocation.args.dry_run,
                echo=invocation.args.verbose
            )
            shell.call(
                [invocation.runner.toolchain.ninja, "install"],
                dry_run=invocation.args.dry_run,
                echo=invocation.args.verbose
            )