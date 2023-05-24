# Documentation for bio_PII

This section likely isn't perfect, but I did my best to explain everything and provide helpful examples. 


### SWA()

Performs sliding window analysis on a 2D NumPy array. Currently, the only supported algorithm is "sum"

**Function Signature**
```python
SWA(image: np.ndarray, windowSize: int, algorithm: str, subImageSize: int = None, GPU: bool = False):
```

**Parameters**
* `image (np.ndarray)`: The 2D numpy array of the image to be analyzed 
* `windowSize (int)`: The size of the window for SWA as an int. Window size must be smaller than subImageSize. 
* `algorithm (str)`: The type of algorithmic analysis to perform on the image
* `subImageSize (int, optional)`: The size of chunks to split the image in to. If not provided, SWA will attempt to perform SWA on the image all at once which may cause memory issue. If provided, it will automatically split the image into chunks and produce the same result as if processed all at once. subImageSize must be bigger than windowSize. Defaults to None.
* `GPU (bool, optional)`: Boolean which controls if the SWA makes use of your machine's GPU; Your GPU must be CUDA compatible. Defaults to False.

**Returns**
`[np.ndarray] or [[np.ndarray], int, int]`

Returns the result of applying sliding window analysis to the passed in image. If you did not split your target image, it will be returned as a 2D numpy array. If you did, it will be returned as a list of the format [chunks, rows, cols where] chunks are the processed sub images, rows are the number of rows of results and cols are the number of cols per row of results.

**Examples**

```python
# perform summing SWA on the target image with a window size of 500 - 
# no split, no GPU
chunks,rows,cols = PII.SWA(image,500,"sum")

# perform summing SWA on the target image with a window size of 250  
# and use the GPU - no split
chunks,rows,cols = PII.SWA(image,250,"sum", GPU=True)

# perform summing SWA on the target image with a window size of 250 
# and split the image up into chunks of 10,000 that fit into my GPU 
# memory
chunks,rows,cols = PII.SWA(image,250,"sum", subImageSize=10000, GPU=True)
```

### save_split_image()

The `save_split_image()` function saves the split image chunks to files in the specified output directory. It provides the option to combine the chunks back into a single file. Note that for massive files, it likely will fail at recombination due to memory constraints. 

**Function Signature**

```python
save_split_image(chunks: [np.ndarray], numRows: int, numCols: int, outDir: str, reconstruct = False) -> None
```

**Parameters**
- `chunks ([np.ndarray])`: List of NumPy arrays representing image chunks.
- `numRows (int)`: Number of rows in the image.
- `numCols (int)`: Number of columns in the image.
- `outDir (str)`: Output directory to save the image chunks.
- `reconstruct (bool, optional)`: Flag indicating whether to reconstruct the image before saving it. Defaults to False.

__Returns__
`None`

__Examples__
```python
# perform summing SWA on the target image with a window size of 250 
# and split the image up into chunks of 10000 that fit into my GPU memory
chunks,numRows,numCols = PII.SWA(image,250,"sum", subImageSize=1000, GPU=True)

# save the chunks in a directory called "out/" as separate files
PII.save_split_image(chunks,numRows,numCols,"out/")

# combine the chunks into a single file and save that file in a 
# directory called "out/"
PII.save_split_image(chunks,numRows,numCols,"out/",reconstruct=True)
```

<br>
<div style="height: 4px; background-color: black;"></div>
<br>

*Note: All functions past here are in the package so that you can use them directly. However, all analysis should be possible (and safer) with the SWA function.* 

## split_image_chunks()

The `split_image_chunks()` function allows you to split an image into chunks for window-based analysis. It utilizes a special splitting method that enables parallel processing without losing any extra dimensionality compared to not splitting the image. This is very helpful to make your chunks fit instead GPU memory and/or also make them small enough that CPU memory can process them. 


__Function Signature__

```python
split_image_chunks(image: np.ndarray, chunkSize: int, windowSize: int) -> [np.ndarray], int, int
```
__Parameters__
* `image (np.ndarray)`: The input image as a NumPy array.
* `chunkSize (int)`: The size of each image chunk.
* `windowSize (int)`: The window size for the analysis.

__Returns__
`[np.ndarray], int, int`: A list of image chunks, along with the number of chunk rows and columns.

__Examples__
```python
# split into chunks of 10,000 with a window size of 50
chunks, numRows, numCols = PII.split_image_chunks(image, 10000, 50)
```

## process_split_image()

The `process_split_image()` function processes the split image chunks using a given siding window algorithm.

**Function Signature**

```python
process_split_image(func: function, windowSize: int, chunks: [np.ndarray], GPU: bool = False) -> [np.ndarray]
```
**Parameters**

* `func (function)`: The function to process the image chunks.
* `windowSize (int)`: The window size for the analysis.
* `chunks ([np.ndarray])`: A list of image chunks as NumPy arrays.
* `GPU (bool, optional)`: Flag indicating whether to use GPU for computation. Defaults to False.

**Returns**

`[np.ndarray]` A list of the processed chunks where each chunk is a `np.ndarray`

__Examples__
```python
# split into chunks of 10,000 with a window size of 500
chunks, numRows, numCols = PII.split_image_chunks(image, 10000, 500)

# process the chunks with the sum algorithm and a window size of 500- CPU only
result_chunks, = PII.process_split_image(PII.sum, 500, chunks)

# process the chunks with the sum algorithm  and a window size of 500- GPU enabled
result_chunks, = PII.process_split_image(PII.sum, 500, chunks, GPU = True)
```

### sum()

**Function Signature**
 `sum(matrix: np.ndarray, windowSize: int, GPU: bool = False) -> np.ndarray`

Perform integral image sum SWA on a 2D matrix. This function calculates the sum of values within a sliding window of a specified size.

**Parameters**
- `matrix` (`np.ndarray`): The input matrix as a NumPy array.
- `windowSize` (`int`): The window size for the sum operation.
- `GPU` (`bool`, optional): Flag indicating whether to use GPU for computation. Defaults to `False`.

**Returns**:
- `np.array`: The result of the sum operation as a NumPy array.

*Notes*
- Make sure you understand the purpose and usage of this function. It is typically used within the SWA function. It is recommended to use the SWA function directly for most use cases.

---

**Example Usage:**

```python
import numpy as np

# Create an example matrix
matrix = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])

windowSize = 2

# sum - no GPU
result = PII.sum(matrix, windowSize)

# sum - use GPU
result = PII.sum(matrix,windowSize,GPU=True)

```

