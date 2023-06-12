from setuptools import setup, find_packages

setup(
    name='BioPII',
    version='0.1.2',
    author='Seth Ockerman',
    author_email='ockermas@mail.gvsu.edu',
    description='BioPII (Biology Parallel Integral Image) is a Python package for performing sliding window analysis (SWA) on biological images.',
    url='https://github.com/OckermanSethGVSU/Bio-PII',
    packages=find_packages(),
    py_modules=['BioPII'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Environment :: GPU :: NVIDIA CUDA',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='Biology, Integral Image, Sliding Window, HPC',
    install_requires=[
        'numpy',
        'opencv-python',
    ],
      extras_require={
        'GPU-Support': ['cupy']
    },
)

