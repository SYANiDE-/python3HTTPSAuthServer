import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python3HTTPSAuthServer",
    version="0.1.1",
    author="Chase Hatch",
    author_email="chase.hatch.business@gmail.com",
    description="Python3-based http.server supporting Basic AUTH and HTTPS; it's SimpleHTTPServer with python3 facial hair! ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SYANiDE-/python3HTTPSAuthServer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	package_dir = {"python3HTTPSAuthServer":"python3HTTPSAuthServer"},
)
