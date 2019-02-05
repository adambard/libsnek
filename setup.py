import setuptools
from Cython.Build import cythonize

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libsnek",
    version="0.0.1",
    author="Adam Bard",
    author_email="libsnek@adambard.com",
    description="Libs for snek",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adambard/libsnek",
    packages=setuptools.find_packages(include=['libsnek']),
    ext_modules=cythonize("libsnek/*.pyx"),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
