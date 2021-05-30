# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument

from typing import Optional, Tuple
from enum import Enum
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, AnyHttpUrl

from starlette.requests import Request
from starlette.responses import Response

from PIL import Image, ImageOps, UnidentifiedImageError

from app.lib import scale_and_crop

import requests
import io

SUPPORTED_FILE_TYPES = ("GIF", "ICO", "JPEG", "PNG")


class FormatEnum(str, Enum):
    """

    """
    gif = 'gif'
    ico = 'ico'
    jpeg = 'jpeg'
    png = 'png'


class ModeEnum(str, Enum):
    rgb = 'rgb'
    rgba = 'rgba'


class ResizeMethods(str, Enum):
    """
Method that will be used when resizing a document, <b>only applicible if either 
width or height values are provided</b>. Optionals available are scale, crop, 
and scale_and_crop.

<ul>
    <li>
        <b>scale</b> 
        Scale the image down with the max width being the width provided and 
        max height being the height provided. Will keep aspect ratio. 
        <a target="_blank" href="">Example</a>
    </li>
    <li>
        <b>crop</b> 
        Crop the image into dimentions provided, default origin point is the 
        top left of the image. Will disturb aspect ratio. 
        <a target="_blank" href="">Example</a>
    </li>
    <li>
        <b>scale_and_crop</b> 
        Scale the image down, then crop the image into a square with the origin 
        being cenetered. Will disturb aspect ratio. 
        <a target="_blank" href="">Example</a>
    </li>
</ul>
    """

    scale = 'scale'
    crop = 'crop'
    scale_and_crop = 'scale_and_crop'


router = APIRouter()


@router.get("/image", )
async def image(
    http_request: Request,

    width: Optional[int] = Query(
        None, gt=0, description="Max width the output image will become, output image will be resized if value is provided."),
    height: Optional[int] = Query(
        None, gt=0, description="Max height the output image will become, output image will be resized if value is provided."),
    resize_method: Optional[ResizeMethods] = Query(
        ResizeMethods.scale, description=ResizeMethods.__doc__),

    greyscale: Optional[bool] = Query(False),

    source: Optional[AnyHttpUrl] = Query(None),

    format: Optional[FormatEnum] = Query(None),
    mode: Optional[ModeEnum] = Query(None),
):
    """
    Main endpoint for the application
    """

    image = None

    in_raw_image = None
    in_image_format = None
    in_image_mode = None

    out_raw_image = None
    out_image_format = None
    out_image_mode = None

    if (source):
        # Getting the image from the source URL
        # provided if it exists
        request = requests.get(source)
        if (200 > request.status_code > 299):
            raise HTTPException(400, "Download from {} failed".format(source))
        in_raw_image = request.content
    else:
        # Getting the image from the request body
        in_raw_image = await http_request.body()

    try:
        bytesio_image = io.BytesIO(in_raw_image)
        if (bytesio_image.getbuffer().nbytes > 20_000_000):
            raise HTTPException(400, "File size exceeded 20Mb")
        image = Image.open(bytesio_image, formats=SUPPORTED_FILE_TYPES)

        in_image_format = image.format
        in_image_mode = image.mode
    except UnidentifiedImageError as e:
        raise HTTPException(415, "Unsupported file type. Supported file types are {}"
                            .format(", ".join(SUPPORTED_FILE_TYPES)))

    if (width or height):
        # Setting the height & width from the image
        # if it isn't already set by the user
        height = height if height else image.height
        width = width if width else image.width

        # Resizing the image based on the
        # resize_method that was provided
        if resize_method == ResizeMethods.scale:
            image.thumbnail((width, height))
        elif resize_method == ResizeMethods.crop:
            image = image.crop((0, 0, width, height))
        elif resize_method == ResizeMethods.scale_and_crop:
            image = scale_and_crop(image, (width, height))

    if (greyscale == True):
        # Grayscale the image if greyscale
        # request param is set to True
        image = ImageOps.grayscale(image)

    out_image_format = in_image_format
    out_image_mode = in_image_mode

    # Saving the image, and converting it
    # into binary, storing that into out_raw_image
    out_raw_image = io.BytesIO()
    image.save(out_raw_image, format=out_image_format)
    out_raw_image = out_raw_image.getvalue()

    return Response(out_raw_image, media_type='image/{}'.format(in_image_format.lower()))
