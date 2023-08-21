import numpy as np
import cv2

windowSize = int(input("Enter window size: "))
cv_image = cv2.imread("../capstone/images/40x40.png")
matrix = cv_image[:, :, 0]


rows, cols = matrix.shape
result = [[0 for _ in range(cols)] for _ in range(rows)]
for i in range(rows - windowSize + 1):
    for j in range(cols - windowSize + 1):    
        sum_x = 0
        sub = [[0 for _ in range(windowSize)] for _ in range(windowSize)]
    
        for y in range(j,j + windowSize):   
            for x in range(i,i + windowSize):
                # sum_x += matrix[x][y]
                
                sub[x - i][y - j] = matrix[x][y]
            
     
        result[i][j] = np.std(sub)
# np.set_printoptions(threshold=np.inf)
result = np.array(result)
print(result[:-(windowSize - 1), : -(windowSize - 1)])