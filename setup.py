#!/usr/bin/env python

from setuptools import setup


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="gcs-signurl",
    version="0.0.3",
    description="Google Cloud Storage URL signer that supports looong expiration dates",
    long_description=readme,
    author="Zaar Hai",
    author_email="haizaar@haizaar.com",
    url="https://github.com/haizaar/gcr-signer",
    license=license,
    packages=["."],
    install_requires=(
        "click",
        "google-cloud-storage",
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={
        "console_scripts": (
            "gcs-signurl=gcs_signurl:sign",
        )
    }
)
