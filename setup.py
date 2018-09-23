from setuptools import setup, find_packages
import sys, os, codecs, re

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

META_FILE = read(os.path.join("asprin", "__init__.py"))

def find_meta(meta):
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))

setup(
    name = find_meta("package"),
    version = find_meta("version"),
    description = find_meta("description"),
    author = find_meta("author"),
    author_email = find_meta("email"),
    url = find_meta("url"),
    license = find_meta("license"),
    long_description = read("README.md"),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console', 
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='logic answer set programming preference optimization',
    packages=find_packages('.'),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'asprin=asprin.asprin:main',
        ],
    },
)
