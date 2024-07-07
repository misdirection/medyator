from setuptools import setup, find_packages

setup(
    name="Medyator",
    version="0.3.1",  # Update the version number
    author="Misdirection",
    author_email="misdirection@live.de",
    description="A command and query mediator for Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/misdirection/medyator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=["typing-extensions", "kink"],
    tests_require=[
        "pytest",
    ],
    setup_requires=["pytest-runner"],
)
