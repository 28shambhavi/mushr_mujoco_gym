import setuptools
import os

# read the long description from README if present
def read(fname):
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, fname), encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

setuptools.setup(
    name="mushr_mujoco_gym",
    version="0.0.1",  # bump version appropriately
    author="28shambhavi (or project authors)",
    author_email="youremail@example.com",
    description="Gym / Mujoco environments for MuSHR car + block",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/28shambhavi/mushr-mujoco-gym",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or whichever license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # adjust as needed
    install_requires=[
        "gymnasium",     # or gym if using older gym
        "mujoco>=3.0.0",  # or whichever version is needed
        # any other dependencies your code uses
    ],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            # etc
        ],
    },
    entry_points={
        # if you have console scripts, e.g.:
        # "console_scripts": [
        #     "mushr-env = mushr_mujoco_gym.cli:main",
        # ],
    },
)
