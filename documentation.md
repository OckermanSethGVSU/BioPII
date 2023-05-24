## `split_image_chunks()`

The `split_image_chunks()` function allows you to split an image into chunks for window-based analysis. It utilizes a special splitting method that enables parallel processing without losing any extra dimensionality compared to not splitting the image.



```python
split_image_chunks(image: np.ndarray, chunkSize: int, windowSize: int) -> [[np.ndarray], int, int]
```