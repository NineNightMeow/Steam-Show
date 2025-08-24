from PIL import Image
import numpy as np

ascii_x_dots = 2
ascii_y_dots = 4


class KernelDitherer:
    def __init__(self, offset, kernel, divisor):
        self.offset = offset
        self.kernel = kernel
        self.divisor = divisor

    def dither(self, image_data, threshold):
        height, width = image_data.shape
        dithered = np.copy(image_data)

        for y in range(height):
            for x in range(width):
                old_pixel = dithered[y, x]
                new_pixel = 255 if old_pixel > threshold else 0
                dithered[y, x] = new_pixel
                error = old_pixel - new_pixel

                for ky, row in enumerate(self.kernel):
                    for kx, value in enumerate(row):
                        ny, nx = y + ky + self.offset[1], x + kx + self.offset[0]
                        if 0 <= ny < height and 0 <= nx < width:
                            dithered[ny, nx] += error * value / self.divisor

        return dithered


ditherers = {
    "threshold": KernelDitherer([0, 0], [], 1),
    "floydSteinberg": KernelDitherer(
        [1, 0],
        [
            [0, 0, 7],
            [3, 5, 1],
        ],
        16,
    ),
    "stucki": KernelDitherer(
        [2, 0],
        [
            [0, 0, 0, 8, 4],
            [2, 4, 8, 4, 2],
            [1, 2, 4, 2, 1],
        ],
        42,
    ),
    "atkinson": KernelDitherer(
        [1, 0],
        [
            [0, 0, 1, 1],
            [1, 1, 1, 0],
            [0, 1, 0, 0],
        ],
        8,
    ),
}


def render(
    image_path,
    ascii_width=100,
    threshold=127,
    invert=False,
    ditherer_name="floydSteinberg",
):

    image = Image.open(image_path).convert("L")
    aspect_ratio = image.height / image.width
    ascii_height = int(ascii_width * ascii_x_dots * aspect_ratio / ascii_y_dots)

    # Resize image
    image = image.resize((ascii_width * ascii_x_dots, ascii_height * ascii_y_dots))
    image_data = np.array(image)

    ditherer = ditherers[ditherer_name]
    dithered_data = ditherer.dither(image_data, threshold)

    target_value = 255 if invert else 0
    ascii_art = []

    for y in range(0, dithered_data.shape[0], ascii_y_dots):
        line = []
        for x in range(0, dithered_data.shape[1], ascii_x_dots):
            char_code = 10240
            char_code += int(dithered_data[y + 3, x + 1] == target_value) << 7
            char_code += int(dithered_data[y + 3, x] == target_value) << 6
            char_code += int(dithered_data[y + 2, x + 1] == target_value) << 5
            char_code += int(dithered_data[y + 1, x + 1] == target_value) << 4
            char_code += int(dithered_data[y, x + 1] == target_value) << 3
            char_code += int(dithered_data[y + 2, x] == target_value) << 2
            char_code += int(dithered_data[y + 1, x] == target_value) << 1
            char_code += int(dithered_data[y, x] == target_value) << 0
            line.append(chr(char_code))
        ascii_art.append("".join(line))

    return "\n".join(ascii_art)
