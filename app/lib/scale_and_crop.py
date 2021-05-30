from typing import Tuple
from PIL import Image


def scale_and_crop(image: Image, resize: Tuple[int, int]):
    """
Scale and crop the image provided and resize it using the resize tuple. Resize 
tuple formatted (width: int, height: int)
    """

    # Copy the image into a newImage variable
    newImage = image.copy()

    # Get the currentWidth and currentHeight from the
    # image and the newWidth and newHeight from the resize tuple
    currentWidth, currentHeight = newImage.size
    newWidth, newHeight = resize

    # Scale the image down
    newImage.thumbnail(
        (currentWidth, newHeight) if (currentWidth >= currentHeight)
        else (newWidth, currentHeight)
    )

    # Updating the currentWidth and currentHeight
    currentWidth, currentHeight = newImage.size

    # Cropping the image down
    return newImage.crop((
        (currentWidth - newWidth) // 2,
        (currentHeight - newHeight) // 2,
        (currentWidth + newWidth) // 2,
        (currentHeight + newHeight) // 2,
    ))
