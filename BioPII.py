import numpy as np
# import cupy as cp
import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2,40))
import cv2

import csv
import time



    
    


class PII:

    @staticmethod
    def SWA(image: np.ndarray, windowSize: int, algorithm: str, subImageSize: int = None, GPU: bool = False):
        """
        Performs sliding window analysis on a 2d numpy array

        Args:
            image (np.ndarray): The 2D numpy array of the image to be analyzed 
            windowSize (int): The size of the window for SWA as an int
            algorithm (str): The type of analysis to perform on the image - currently only sum is supported
            subImageSize (int): In the event that the target image is too big to process at once (either by the CPU or GPU),
                                the image should be split up into smaller sizes. This controls the size of the sub image.
                                Defaults to none.
            GPU (bool): Boolean which controls if the SWA makes use of your machine's GPU; Your GPU must be CUDA compatible.
                        Defaults to False.

        Returns:
            return_type: the result of applying sliding window analysis to the passed in image. If you did not split your
                         target image, it will be returned as a 2D numpy array. If you did, it will be returned as a list
                         of the format [chunks, rows , cols] where chunks are the processed sub images, rows are the number
                         of rows of results and cols are the number of cols per row of results

        Raises:
            Type Error: Raised when an invalid parameter type was passed in
            Value Error: Raised when the wrong shape of numpy array is passed in

        Examples:
            Perform sum SWA on a image using a window size of 500 - no split and no GPU: PII.SWA(image,500,"sum")
            Perform sum SWA on a image using a window size of 10 - no split and GPU: PII.SWA(image,10,"sum",GPU=True)
            Perform sum SWA on a image using a window size of 75 - split and GPU: PII.SWA(image,75,"sum",subImageSize=10000,GPU=True)
   
        """

        # error checking
        if not isinstance(image,np.ndarray):
            raise TypeError("Invalid type for 'image'. Expected np.array.")
        if image.ndim != 2:
            raise ValueError("Invalid shape for 'image'. Expected 2D array.")
        if not isinstance(windowSize, int):
            raise TypeError("Invalid type for 'windowSize'. Expected int.")
        if not isinstance(algorithm, str):
            raise TypeError("Invalid type for 'analysisType'. Expected str.")
        if subImageSize is not None and not isinstance(subImageSize, int):
            raise TypeError("Invalid type for 'subImageSize'. Expected int.")
        if subImageSize is not None and windowSize > subImageSize:
            raise ValueError("'SubImageSize' must be greater than 'windowSize'")
        if image.shape[0] < windowSize or image.shape[1] < windowSize:
            raise ValueError("Image dimensions must be greater than windowSize.")
        if subImageSize is not None and (image.shape[0] < subImageSize or image.shape[1] < subImageSize):
            raise ValueError("Image dimensions must be greater than subImageSize.")
        if not isinstance(GPU, bool):
            raise TypeError("Invalid type for 'GPU'. Expected bool.")



        if subImageSize != None:
            return PII.__multi_image_integral_analysis(image, subImageSize, windowSize,  algorithm, GPU=GPU)
            
        else:
            return PII.__single_image_integral_analysis(image, windowSize, algorithm, GPU=GPU)
    
    @staticmethod
    def split_image(image: np.ndarray, chunkSize: int, windowSize: int) -> [[np.ndarray], int, int]:
        """
        Split an image into chunks for window-based analysis. Uses a special splitting method
        to allow the chunks to be process in parallel and without losing any extra dimensionality
        compared to if you had not split the image. 

        Args:
            image (np.ndarray): The input image as a NumPy array.
            chunkSize (int): The size of each image chunk.
            windowSize (int): The window size for the analysis.

        Returns:
            [[np.array], int, int]: A list of image chunks, along with the row count and column count.
        """
        if not isinstance(image, np.ndarray):
            raise TypeError("Invalid type for 'image'. Expected np.array.")
        if image.ndim != 2:
            raise ValueError("Invalid shape for 'image'. Expected 2D array.")
        if not isinstance(chunkSize, int):
            raise TypeError("Invalid type for 'chunkSize'. Expected int.")
        if not isinstance(windowSize, int):
            raise TypeError("Invalid type for 'windowSize'. Expected int.")



        # setup variables
        rows, cols = image.shape
        i,j = 0,0
        i_collection = []
        j_collection = []
        chunks = []

        # split image in sub-images
        while (i * chunkSize) - (i * (windowSize - 1)) < rows :
            while (j * chunkSize) - (j * (windowSize - 1)) < cols:
               
                # calculate slice 
                startCol = (chunkSize * j) - (j * (windowSize - 1))
                startRow = (chunkSize * i) - (i * (windowSize - 1))
                endRow = startRow + chunkSize
                endCol = startCol + chunkSize

                chunk = image[startRow:endRow, startCol:endCol]
                chunks.append(chunk)
                i_collection.append(i)
                j_collection.append(j)
                j += 1

                # if we happened to exactly hit the last column - break the inner loop and move on to next row
                if endCol == cols:  
                    break
            # if we hit exactly the last row and column - splitting is over, so break
            if endCol == cols and endRow == rows:
                break   
            i += 1
            j = 0
        
        # return the split image and the number of rows and columns in the splits
        return chunks, max(i_collection), max(j_collection)
        

    @staticmethod
    def process_split_image(func, windowSize: int,  chunks: [np.ndarray], GPU: bool = False) -> [np.ndarray]:
        """
        Process the split image chunks using a given function

        Args:
            func (function): The function to process the image chunks.
            windowSize (int): The window size for the analysis.
            chunks (List[np.ndarray]): A list of image chunks as NumPy arrays.
            GPU (bool, optional): Flag indicating whether to use GPU for computation. Defaults to False.

        Returns:
            A list of the processed chunks
        """
        if not isinstance(windowSize, int):
            raise TypeError("Invalid type for 'windowSize'. Expected int.")
        if not isinstance(chunks, list):
            raise TypeError("Invalid type for 'chunks'. Expected list.")
        if not all(isinstance(chunk, np.ndarray) for chunk in chunks):
            raise TypeError("Invalid type for elements in 'chunks'. Expected np.array.")
        if not isinstance(GPU, bool):
            raise TypeError("Invalid type for 'GPU'. Expected bool.")
        
        results = []
        for i in range(len(chunks)):
            matrix = chunks[i]
            method = getattr(PII, func)
            results.append(method(matrix, windowSize, GPU=GPU))
        
        return results
      
    
    @staticmethod
    def save_split_image(chunks: [np.ndarray], numRows: int, numCols: int, outDir: str, reconstruct = False) -> None:
        """
        Save the split image chunks to files in the specified output directory.

        Args:
            chunks (List[np.ndarray]): List of numpy arrays representing image chunks.
            numRows (int): Number of rows in the image.
            numCols (int): Number of columns in the image.
            outDir (str): Output directory to save the image chunks.
            reconstruct (bool, optional): Flag indicating whether to reconstruct the image before saving it. Defaults to False.

        Returns:
            None
        """
        if not isinstance(chunks, list):
            raise TypeError("Invalid type for 'chunks'. Expected list.")
        if not all(isinstance(chunk, np.ndarray) for chunk in chunks):
            raise TypeError("Invalid type for elements in 'chunks'. Expected np.ndarray.")
        if not isinstance(numRows, int):
            raise TypeError("Invalid type for 'numRows'. Expected int.")
        if not isinstance(numCols, int):
            raise TypeError("Invalid type for 'numCols'. Expected int.")
        if not isinstance(outDir, str):
            raise TypeError("Invalid type for 'outDir'. Expected str.")
        if not isinstance(reconstruct, bool):
            raise TypeError("Invalid type for 'reconstruct'. Expected bool.")
        
        if not os.path.exists(outDir):
            os.makedirs(outDir)

        index = 0

        if reconstruct:
            cv2.imwrite(f"{outDir}output.tif", PII.reconstruct_image(chunks,numRows, numCols))
        else:
            for i in range(numRows + 1):
                for j in range(numCols+ 1):
                    subImage = chunks[index]
                    if subImage.size != 0:
                        cv2.imwrite(f"{outDir}result-row-{i}-col-{j}.tif", subImage)
                    index+=1


            


    @staticmethod
    def sum(matrix: np.ndarray, windowSize: int, GPU: bool = False) -> np.ndarray:
        """
        Perform integral image sum SWA on 2d matrix. Make sure you know what you are doing
        if you are calling this outside of the SWA function - you should be able to do all 
        you need with just SWA. 

        Args:
            matrix (np.ndarray): The input matrix as a NumPy array.
            windowSize (int): The window size for the sum operation.
            GPU (bool, optional): Flag indicating whether to use GPU for computation. Defaults to False.

        Returns:
            np.array: The result of the sum operation as a NumPy array.
        """
        if not isinstance(matrix, np.ndarray):
            raise TypeError("Invalid type for 'matrix'. Expected np.array.")
        if matrix.ndim != 2:
            raise ValueError("Invalid shape for 'image'. Expected 2D array.")
        if not isinstance(windowSize, int):
            raise TypeError("Invalid type for 'windowSize'. Expected int.")
        if not isinstance(GPU, bool):
            raise TypeError("Invalid type for 'GPU'. Expected bool.")



        if not GPU:
            # calculate integral image
            integralImage = np.cumsum(np.cumsum(matrix, axis=0), axis=1)
            """
             Pad the integral image so we don't lose any dimensionality, and then
             compute the sum of each window using the integral image formula
             
             sum of bottom right + sum of top left - sum of button left - sum of top right
             """
            paddedIntegralImage = np.pad(integralImage, ((windowSize, 0), (windowSize, 0)), mode='constant')
            windowSum = paddedIntegralImage[windowSize:, windowSize:] + paddedIntegralImage[:-windowSize, :-windowSize] - \
                        paddedIntegralImage[windowSize:, :-windowSize] - paddedIntegralImage[:-windowSize, windowSize:]

            # slice off extra from padding - may be causing an error with massive window sizes - need to check a few edge cases
            windowSum = windowSum[windowSize - 1:, windowSize - 1:]
            return windowSum

        elif GPU:

            
            # convert to CUPY array and calculate the integral image
            gpuMatrix = cp.asarray(matrix)
            integralImage = cp.cumsum(cp.cumsum(gpuMatrix, axis=0), axis=1)
            """
            Pad the integral image so we don't lose any dimensionality, and then
            compute the sum of each window using the integral image formula
            
            sum of bottom right + sum of top left - sum of button left - sum of top right
            """
            paddedIntegralImage = cp.pad(integralImage, ((windowSize, 0), (windowSize, 0)), mode='constant')
            windowSum = paddedIntegralImage[windowSize:, windowSize:] + paddedIntegralImage[:-windowSize, :-windowSize] - \
                        paddedIntegralImage[windowSize:, :-windowSize] - paddedIntegralImage[:-windowSize, windowSize:]

            # slice off extra from padding - may be causing an error with massive window sizes - need to check a few edge cases
            windowSum = windowSum[windowSize - 1:, windowSize - 1:]
    
            return windowSum.get()
        


    @staticmethod
    def avg(matrix: np.ndarray, windowSize: int, GPU: bool = False) -> np.ndarray:
        """
        Perform integral image avg SWA on 2d matrix. Make sure you know what you are doing
        if you are calling this outside of the SWA function - you should be able to do all 
        you need with just SWA. 

        Args:
            matrix (np.ndarray): The input matrix as a NumPy array.
            windowSize (int): The window size for the sum operation.
            GPU (bool, optional): Flag indicating whether to use GPU for computation. Defaults to False.

        Returns:
            np.array: The result of the avg operation as a NumPy array.
        """
        if not isinstance(matrix, np.ndarray):
            raise TypeError("Invalid type for 'matrix'. Expected np.array.")
        if matrix.ndim != 2:
            raise ValueError("Invalid shape for 'image'. Expected 2D array.")
        if not isinstance(windowSize, int):
            raise TypeError("Invalid type for 'windowSize'. Expected int.")
        if not isinstance(GPU, bool):
            raise TypeError("Invalid type for 'GPU'. Expected bool.")



        if not GPU:
            # calculate integral image
            integralImage = np.cumsum(np.cumsum(matrix, axis=0), axis=1)
            """
             Pad the integral image so we don't lose any dimensionality, and then
             compute the sum of each window using the integral image formula
             
             sum of bottom right + sum of top left - sum of button left - sum of top right
             """
            paddedIntegralImage = np.pad(integralImage, ((windowSize, 0), (windowSize, 0)), mode='constant')
            windowSum = paddedIntegralImage[windowSize:, windowSize:] + paddedIntegralImage[:-windowSize, :-windowSize] - \
                        paddedIntegralImage[windowSize:, :-windowSize] - paddedIntegralImage[:-windowSize, windowSize:]

            # slice off extra from padding - may be causing an error with massive window sizes - need to check a few edge cases
            windowSum = (windowSum[windowSize - 1:, windowSize - 1:]) / (windowSize * windowSize)
            return windowSum

        elif GPU:

            
            # convert to CUPY array and calculate the integral image
            gpuMatrix = cp.asarray(matrix)
            integralImage = cp.cumsum(cp.cumsum(gpuMatrix, axis=0), axis=1)
            """
            Pad the integral image so we don't lose any dimensionality, and then
            compute the sum of each window using the integral image formula
            
            sum of bottom right + sum of top left - sum of button left - sum of top right
            """
            paddedIntegralImage = cp.pad(integralImage, ((windowSize, 0), (windowSize, 0)), mode='constant')
            windowSum = paddedIntegralImage[windowSize:, windowSize:] + paddedIntegralImage[:-windowSize, :-windowSize] - \
                        paddedIntegralImage[windowSize:, :-windowSize] - paddedIntegralImage[:-windowSize, windowSize:]

            # slice off extra from padding - may be causing an error with massive window sizes - need to check a few edge cases
            windowSum = (windowSum[windowSize - 1:, windowSize - 1:]) / (windowSize * windowSize)
    
            return windowSum.get()

    @staticmethod
    def std(matrix: np.ndarray, windowSize: int, GPU: bool = False) -> np.ndarray:
        """
        Perform integral image std SWA on 2d matrix. Make sure you know what you are doing
        if you are calling this outside of the SWA function - you should be able to do all 
        you need with just SWA. 

        Args:
            matrix (np.ndarray): The input matrix as a NumPy array.
            windowSize (int): The window size for the sum operation.
            GPU (bool, optional): Flag indicating whether to use GPU for computation. Defaults to False.

        Returns:
            np.array: The result of the avg operation as a NumPy array.
        """
        if not isinstance(matrix, np.ndarray):
            raise TypeError("Invalid type for 'matrix'. Expected np.array.")
        if matrix.ndim != 2:
            raise ValueError("Invalid shape for 'image'. Expected 2D array.")
        if not isinstance(windowSize, int):
            raise TypeError("Invalid type for 'windowSize'. Expected int.")
        if not isinstance(GPU, bool):
            raise TypeError("Invalid type for 'GPU'. Expected bool.")



        if not GPU:

            # Compute summed area table
            integralImage = np.cumsum(np.cumsum(matrix, axis=0), axis=1)

            # calculate the average of each window
            paddedIntegralImage = np.pad(integralImage, ((windowSize, 0), (windowSize, 0)), mode='constant')
            windowSum = paddedIntegralImage[windowSize:, windowSize:] + paddedIntegralImage[:-windowSize, :-windowSize] - \
                        paddedIntegralImage[windowSize:, :-windowSize] - paddedIntegralImage[:-windowSize, windowSize:]
            temp = windowSum[windowSize - 1:, windowSize - 1:]
            mean = temp / (windowSize ** 2)

            # Get each of the windows into an array that we can subtract the mean from it
            num_rows, num_cols = matrix.shape[0], matrix.shape[1]
            num_valid_rows = np.maximum(0, num_rows - windowSize + 1)
            num_valid_cols = np.maximum(0, num_cols - windowSize + 1)
            shape = (num_valid_rows, num_valid_cols, windowSize, windowSize)
            strides = matrix.strides * 2
            windows = np.lib.stride_tricks.as_strided(matrix, shape=shape, strides=strides)

            # square the differences and then add them up
            sqr_diff = (windows - mean[:, :, np.newaxis, np.newaxis]) ** 2
            sum_matrix = np.sum(sqr_diff, axis=(-2, -1))

            # get the avg of each of those differences            
            avg_sum_diffs = sum_matrix / (windowSize ** 2)

            # sqrt to get std-dev
            return np.sqrt(avg_sum_diffs)
      
            

        elif GPU:
            
            # convert to GPU memory
            gpuMatrix = cp.asarray(matrix)

            # Compute summed area table
            integralImage = cp.cumsum(np.cumsum(gpuMatrix, axis=0), axis=1)

            # calculate the average of each window
            paddedIntegralImage = cp.pad(integralImage, ((windowSize, 0), (windowSize, 0)), mode='constant')
            windowSum = paddedIntegralImage[windowSize:, windowSize:] + paddedIntegralImage[:-windowSize, :-windowSize] - \
                        paddedIntegralImage[windowSize:, :-windowSize] - paddedIntegralImage[:-windowSize, windowSize:]
            temp = windowSum[windowSize - 1:, windowSize - 1:]
            mean = temp / (windowSize ** 2)

            # Get each of the windows into an array that we can subtract the mean from it
            numRows, numCols = matrix.shape[0], matrix.shape[1]
            numValidRows = cp.maximum(0, numRows - windowSize + 1)
            numValidCols = cp.maximum(0, numCols - windowSize + 1)
            shape = (numValidRows, numValidCols, windowSize, windowSize)
            strides = gpuMatrix.strides * 2
            windows = cp.as_strided(gpuMatrix, shape=shape, strides=strides)

            # square the differences and then add them up
            sqr_diff = (windows - mean[:, :, cp.newaxis, cp.newaxis]) ** 2
            sum_matrix = cp.sum(sqr_diff, axis=(-2, -1))

            # get the avg of each of those differences            
            avg_sum_diffs = sum_matrix / (windowSize ** 2)

            # sqrt to get std-dev
            return (cp.sqrt(avg_sum_diffs)).get()
      

    

    @staticmethod
    def reconstruct_image(chunks: [np.ndarray], rows: int, cols: int):
        """
        Reconstruct the image from the given chunks.

        Args:
            chunks (List[np.ndarray]): List of numpy arrays representing image chunks.
            rows (int): Number of rows of chunks.
            cols (int): Number of columns per chunk row.

        Returns:
            None
        """
        if not isinstance(chunks, list):
            raise TypeError("Invalid type for 'chunks'. Expected list.")
        if not all(isinstance(chunk, np.ndarray) for chunk in chunks):
            raise TypeError("Invalid type for elements in 'chunks'. Expected np.ndarray.")
        if not isinstance(rows, int):
            raise TypeError("Invalid type for 'rows'. Expected int.")
        if not isinstance(cols, int):
            raise TypeError("Invalid type for 'cols'. Expected int.")

        reconstructed_image = []
        chunkNum = 0
        for i in range(rows + 1):
                row = []
                for j in range(cols + 1):
                    result = chunks[chunkNum]
                    chunkNum += 1
                    
                    if j == 0:
                        row = result
                    
                    else:
                        row = np.hstack((row, result))

                if i == 0:
                    reconstructed_image = row
            
                else:
                    reconstructed_image = np.vstack((reconstructed_image,row)) 
                    
        return reconstructed_image 
    
    @staticmethod
    def __single_image_integral_analysis(image,windowSize,analysisType,GPU=False):
        # control function for single image analysis
        match analysisType:
            case "sum":
                return PII.sum(image, windowSize,GPU=GPU)
            case "avg":
                return PII.avg(image,windowSize,GPU=GPU)
            case "std":
                return PII.std(image,windowSize,GPU=GPU)
            case _:
                raise ValueError("Please provide a valid analysis type \nOptions: 'sum','avg','std'")

    @staticmethod
    def __multi_image_integral_analysis(image,chunkSize,windowSize, analysisType,GPU=False):
        # control function for multi image analysis
        chunks,max_i,max_j = PII.split_image(image,chunkSize, windowSize)
    
        match analysisType:
            case "sum":
                return [PII.process_split_image("sum", windowSize,chunks,GPU=GPU),max_i,max_j]
            case "avg":
                return [PII.process_split_image("avg", windowSize,chunks,GPU=GPU),max_i,max_j]
            case "std":
                return [PII.process_split_image("std",windowSize,chunks,GPU=GPU), max_i,max_j]
            case _:
                raise ValueError("Please provide a valid analysis type \nOptions: 'sum','avg','std'")