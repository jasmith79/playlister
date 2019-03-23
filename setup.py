import os.path
import setuptools
import subprocess

with open("README.md") as f:
    long_description = f.read()

version = subprocess.check_output([
    "git",
    "--git-dir",
    os.path.join(os.path.dirname(__file__), ".git"),
    "tag"
]).decode("utf-8").strip().split("\n")[-1]

current_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(current_dir, "playlister", "__version__.py"), "w") as f:
    f.write("version = \"{}\"".format(version))

url = subprocess.check_output([
    "git",
    "--git-dir",
    os.path.join(os.path.dirname(__file__), ".git"),
    "config",
    "--get",
    "remote.origin.url"
]).decode("utf-8").strip()

setuptools.setup(
    name="playlister-jasmith79",
    version=version,
    author="jasmith79",
    author_email="jasmith79@gmail.com",
    description="ITunes® Playlist Converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    packages=["playlister"],
    python_requires='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        "console_scripts": [
            "playlister = playlister.app:main"
        ]
    }
)