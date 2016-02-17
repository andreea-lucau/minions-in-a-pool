import distutils.cmd


import setuptools.command.build_py
from setuptools import setup, find_packages


class BuildWithLintCommand(setuptools.command.build_py.build_py):
    """Custom build command."""

    def run(self):
        self.run_command('lint')
        setuptools.command.build_py.build_py.run(self)


setup(
    name="minions",
    version="1.0",
    description="Example for thread pool used for executing tasks",
    author="Andreea Lucau",
    author_email="andreea.lucau@gmail.com",
    url="https://github.com/andreea-lucau/minions-in-a-pool",
    packages=find_packages("src"),
    package_dir = {
        "": "src",
    },
    install_requires=[
        "pylint",
        "setuptools",
        "setuptools-lint",
    ],
    cmdclass={
        'build_py': BuildWithLintCommand,
    },
)
