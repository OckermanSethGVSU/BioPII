# BioPII

BioPII (Biology Parallel Integral Image) is a Python package for performing sliding window analysis (SWA) on biological images. This package makes use of the integral image technique to drastically speedup SWA, enabling SWA analysis of images that would have been too large for previous SWA implementations. 

To use the package include the following statement at the top of your file: `from BioPII import PII`

To cite this package, cite [the preprint of our IEEE CIBCB 2023 short paper](https://arxiv.org/abs/2410.16291).

```
@misc{ockerman2024acceleratingbiologicalspatialcluster,
      title={Accelerating Biological Spatial Cluster Analysis with the Parallel Integral Image Technique}, 
      author={Seth Ockerman and Zachary Klamer and Brian Haab},
      year={2024},
      eprint={2410.16291},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2410.16291}, 
}
```

 The short paper itself is available on the [IEEE CIBCB 2023](https://cmte.ieee.org/cis-bbtc/wp-content/uploads/sites/172/IEEE_CIBCB_2023_paper_2015.pdf) website. 


This code and package is under the MIT License - copyright (c) Seth Ockerman

The package name is prounounced bio-pie :)

## Performance Numbers
We tested our summing SWA to determine its performance relative to past methods. We created a C++ SWA (referred to as DP-Naive) script which used dynamic programming to reduce the number of additions needed to be performed. DP-Naive SWA was already 400x faster than a naive approach (a simple four for loop approach) on small images and is used as the baseline for comparison to our integral-image-based methods. 

|                   | 30k by 30k | 30k by 30k Speedup | 40k by 50k | 40k by 50k Speedup | 60k by 60k | 60k by 60k Speedup |
|-------------------|------------|--------------------|------------|--------------------|------------|--------------------|
| **DP-Naive**      | 211,381,433| N/A                | 491,374,150| N/A                | 943,858,845     | N/A                |
| **Integral Image**            | 56,693     | 3728x              | 253,082    | 1942x               | 319,666    | 2953x               |
| **Parallel Integral Image**           | 20,137     | 10,497x             | 46,532     | 10,559x             | 86,583    | 10,901x            |

*Note: SWA runtime in milliseconds on different image sizes; speedups relative to DP-Naive Solution*


## Features

- Efficient computation for various biological image analysis tasks.
- Supports different types of SWA (Sliding Window Analysis) algorithms.
- Flexible window size selection for analyzing different cellular features.
- GPU acceleration option for faster computations.
- Works with numpy arrays for easy integration into existing workflows.

## Installation

You can install BioPII using pip:

``` pip3 install BioPII ```

## Documentation
Documentation can be found internally within our code and in the [documentation file](./documentation.md).  


### Note
The average-SWA-algorithm and std-deviation-SWA algorithm have not been as tested as extensively as the sum-SWA-algorithm. If you discover a bug, please reach out to [sockerman@cs.wisc.edu](mailto:sockerman@cs.wisc.edu).
