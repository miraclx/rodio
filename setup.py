import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rodio",
    version="1.0.0",
    author="Miraculous Owonubi",
    author_email="omiraculous@gmail.com",
    description="Efficient non-blocking event loops for async concurrency and I/O",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache-2.0',
    url="https://github.com/miraclx/node-buffer",
    packages=['rodio', 'rodio.internals'],
    install_requires=['node-events', 'uvloop', 'dill'],
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
)
