#!/usr/bin/env python3
"""
Setup script for pysui-client
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pysui-client",
    version="1.0.0",
    author="Sui Client Developer",
    author_email="developer@example.com",
    description="A Sui blockchain client using JSON-RPC interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pysui-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pysui-client=quick_start:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.toml", "*.move"],
    },
)
