from pathlib import Path
from matplotlib.image import imread, imsave
import random

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

class Img:
    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        img_data = imread(path)

        if len(img_data.shape) == 3:  # RGB image
            img_data = rgb2gray(img_data)

        self.data = img_data.tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res

    def rotate(self):
        self.data = list(zip(*self.data[::-1]))

    def salt_n_pepper(self, salt_prob=0.01, pepper_prob=0.01):
        """
        Add salt and pepper noise to the image.

        Args:
        salt_prob (float): Probability of a pixel getting set to max intensity (salt).
        pepper_prob (float): Probability of a pixel getting set to min intensity (pepper).
        """
        height = len(self.data)
        width = len(self.data[0])
        for i in range(height):
            for j in range(width):
                rand_val = random.random()  # Generate a random number between 0 and 1
                if rand_val < salt_prob:
                    self.data[i][j] = 255  # Set pixel to white (salt)
                elif rand_val < salt_prob + pepper_prob:
                    self.data[i][j] = 0  # Set pixel to black (pepper)

    def concat(self, other_img, direction='horizontal'):
        """
        Concatenate another image to this image either horizontally or vertically.

        Args:
        other_img (Img): Another image object to concatenate.
        direction (str): 'horizontal' or 'vertical', the direction of concatenation.
        """
        # Validate dimensions based on the direction of concatenation
        if direction == 'horizontal':
            # Ensure both images have the same height
            if len(self.data) != len(other_img.data):
                raise ValueError("Images must have the same height for horizontal concatenation.")

            # Concatenate each row
            self.data = [row1 + row2 for row1, row2 in zip(self.data, other_img.data)]

        elif direction == 'vertical':
            # Ensure both images have the same width
            if any(len(row1) != len(row2) for row1, row2 in zip(self.data, other_img.data)):
                raise ValueError("Images must have the same width for vertical concatenation.")

            # Concatenate whole images
            self.data.extend(other_img.data)

        else:
            raise ValueError("Direction must be either 'horizontal' or 'vertical'")


    def segment(self):
        if not self.data:
            raise RuntimeError("Image data is empty")

            # Define a threshold value to determine if two pixels are similar
        threshold = 10

        # Initialize a list to store the segments
        segments = []

        # Function to check if two pixel values are similar
        def is_similar(pixel1, pixel2):
            return abs(pixel1 - pixel2) < threshold

        # Function to find the segment index of a given pixel
        def find_segment(pixel):
            for i, segment in enumerate(segments):
                if is_similar(segment[0][2], pixel):
                    return i
            return None

        # Iterate through each pixel in the image
        for y, row in enumerate(self.data):
            for x, pixel in enumerate(row):
                segment_index = find_segment(pixel)
                if segment_index is not None:
                    segments[segment_index].append((x, y, pixel))
                else:
                    # Create a new segment
                    segments.append([(x, y, pixel)])  # Store pixel value along with coordinates

        # Generate a new image where each segment is represented by a unique color
        new_image = [[0] * len(row) for row in self.data]

        # Assign a unique color to each segment
        for i, segment in enumerate(segments):
            color = 0 if segment[0][2] < 128 else 255  # Assign black for darker segments and white for lighter segments
            for x, y, _ in segment:
                new_image[y][x] = color

        # Update the image data
        self.data = new_image

    # Instantiate the Img class with the path to your image file
my_img = Img(r'C:\Users\ronel\PythonProject1/polybot/test/beatles.jpeg')

    # Perform operations on the image
my_img.blur()
my_img.contour()
my_img.concat(my_img, direction='horizontal')
    # You can perform other operations as needed

    # Save the modified image
saved_path = my_img.save_img()









