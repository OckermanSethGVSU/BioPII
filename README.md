# Bio_PII

Bio_PII (Biology Parallel Integral Image) is a Python package for performing sliding window analysis (SWA) on biological images. This package makes use of the integral image technique to drastically speedup SWA, enabling SWA analysis of images that would have been too large for previous SWA implementations. 

To cite this package, cite our [IEEE CIBCB 2023 short paper](TODO). 


This code and package is under the MIT License - copyright (c) Seth Ockerman

The package name is prounounced bio-pie-squared :)

## Performance Numbers
We tested our methods to determine its performance relative to past methods. We created a C++ SWA (refered to as DP-Naive) script which used dynamic programming to reduce the number of additions needed to be performed. DP-Naive SWA was already 400x faster than a naive approach (a simple 4 for loop approach) on small images and is used as the baseline for comparision to our bio-PII methods. 

|                   | 30k by 30k | 30k by 30k Speedup | 40k by 50k | 40k by 50k Speedup | 50k by 65k | 50k by 60k Speedup |
|-------------------|------------|--------------------|------------|--------------------|------------|--------------------|
| **DP-Naive**      | 211,381,433| N/A                | TODO       | N/A                | TODO       | N/A                |
| **II**            | 56,693     | 3728x              | 714,857    | TODO               | 896,572    | TODO               |
| **PII**           | 55,976     | 3776x              | 84,833     | TODO               | 151,796    | TODO               |

*Note: SWA runtime in milliseconds on different image sizes; speedups relative to DP-Naive Solution*


## Features

- Efficient computation for various biological image analysis tasks.
- Supports different types of SWA (Sliding Window Analysis) algorithms.
- Flexible window size selection for analyzing different cellular features.
- GPU acceleration option for faster computations.
- Works with numpy arrays for easy integration into existing workflows.

## Installation

You can install bio PII using pip:

``` pip3 install Bio_PII ```

## Documentation
Documentation can be found internally within our code and in the [documentation file](./documentation.md).  
