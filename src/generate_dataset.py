# -*- coding: utf-8 -*-

import os
import csv, json
import random
import argparse
import uuid
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Ignore deprecation warning 
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# Save individual image to the save dir
def save_img(image: Image, char: str, save_dir: str) -> str:
    """    
    Saves the given image to a file in the specified directory.

    Args:
        image (PIL.Image): The image to be saved.
        char (str): The current character label.
        save_dir (str): The directory to save the image file in.

    Returns:
        str: The filename of the saved image.

    Raises:
        IOError: If there is an error saving the image file.    
    """
    try:
        file_name = f"{uuid.uuid4()}.png"
        image.save(os.path.join(save_dir, file_name))        
        add_to_label(file_name, char)
    except IOError as e:
        print(f"ERROR: {e}")

    return file_name


# Add image name and image label to a csv|json file
def add_to_label(images_id: str, image_label:str) -> None:
    """
    This function adds an image ID column to a CSV label file.

    Args:
        images_id (str): The id|filename of the images.
        image_label (str): The label of the image file text content.

    Returns:
        None.
    """

    # Define the directory where your files are stored
    label_dir = "../data/labels"

    # Define the name of the CSV and JSON files you want to create
    csv_file = os.path.join(label_dir, r"labels.csv")
    json_file = os.path.join(label_dir, r"labels.json")

    # Create the save path if it doesn"t exist
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)    
 
    # Check if the CSV file already exists
    csv_exists = os.path.exists(csv_file)

    # Open the CSV file in append mode and add the new row
    with open(csv_file, mode="a+", newline="", encoding="utf8") as file:
        writer = csv.writer(file)
    
        # Write the header row if the CSV file is empty
        if not csv_exists:
            writer.writerow(["filename", "character"])
    
        # Append the new row to the CSV file
        writer.writerow([images_id, image_label])

    # Writting to json file

    # Check if the file exists, if not create it
    if not os.path.exists(json_file):
        with open(json_file, "w") as file:
            json.dump([], file)

    # Load the JSON file
    with open(json_file, "r") as file:
        data = json.load(file)

    # Add a new item to the list
    data.append({"filename": images_id, "character": image_label})

    # Save the updated data to the file
    with open(json_file, "w") as file:
        json.dump(data, file)

def apply_noise_variations(image) -> list:
    """
    Apply Gaussian, salt, and pepper noise to the given image and return the noisy images.
    
    Args:
    - image: a PIL Image object
    
    Returns:
    - a list of PIL Image objects representing the noisy images
    """
    # todo: Implement this method
    pass


# Add blur effect to image including Gaussian, Motion blur and other OCR-related blurs with various radii
def apply_blur_variations(image) -> list:
    """
    Apply Gaussian, motion, and other OCR-related blurs to the given image and return the blurred images.
    
    Args:
    - image: a PIL Image object
    
    Returns:
    - a list of PIL Image objects representing the blurred images
    """
    blurred_images = []
    input_image = np.asarray(image)
    
    # Apply Gaussian blur with various radii
    for radius in [1, 2, 3]:
        blurred_images.append(image.filter(ImageFilter.GaussianBlur(radius)))
    
    # Apply motion blur with various angles and distances        
    for angle in [0, 45, 90, 135]:
        for distance in [3, 5, 7]:
            # Generate the motion blur kernel
            angle_rad = np.deg2rad(angle)
            kernel_size = int(distance) * 2 + 1
            kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
            cx, cy = (kernel_size-1)/2, (kernel_size-1)/2
            for x in range(kernel_size):
                for y in range(kernel_size):
                    x0, y0 = x-cx, y-cy
                    x1 = x0*np.cos(angle_rad) + y0*np.sin(angle_rad)
                    y1 = -x0*np.sin(angle_rad) + y0*np.cos(angle_rad)
                    if abs(x1) < abs(distance) and abs(y1) < abs(distance):
                        kernel[y, x] = 1.0 / (2.0 * abs(distance))

            # Normalize the kernel
            kernel_sum = np.sum(kernel)
            if kernel_sum > 0:
                kernel /= kernel_sum

            # Apply the motion blur filter to the input image
            output_image = cv2.filter2D(input_image, -1, kernel)

            # Convert the output array back to Image
            output_image = Image.fromarray(output_image)

            # Append the blurred image to the list
            blurred_images.append(output_image)            

    
    # Apply other OCR-related blurs
    # for radius in [1, 2, 3]:
    #     kernel = ImageFilter.Kernel((radius, radius), [1] * (radius * radius))
    #     blurred_images.append(image.filter(kernel))
        
    return blurred_images


# Make variations of each image from generated images
def make_variation(image: Image, char: str, save_path: str) -> None:
    """
    Creates a variation of an image with different blurriness and noise.

    Args:
        image (PIL.Image): The image to be used as an input for the variation.
        char (str): The current character label.
        save_path (str): The path to save the image to.

    Returns:
        None: This function doesn"t return anything. The generated images are saved to the specified directory.

    Raises:
        FileNotFoundError: If the font directory specified by `font_path` doesn"t exist.
    """
    # todo: make variation and for each variation call save() method 
    # save_img(image, char, save_path)
    blur_variations = apply_blur_variations(image)
    
    # Save the original image before making variation
    save_img(image, char, save_path)

    # Save each images in the variation
    for img in blur_variations:
        save_img(img, char, save_path)    


# Generate a list of images
def generate_img(characters, font_dir, font_sizes, bg_colors, font_colors, save_path) -> None:
    """
     Generate an image with a single character drawn on it with a given font and color.

    Args:
        characters (str): The character to draw on the image.
        font_dir (str): The path to the TrueType font file to use.
        font_size (int): The font size to use.
        bg_color (list(Tuple[int, int, int])): The background color of the image as a tuple of RGB values.
        font_color (list((Tuple[int, int, int])): The color of the font as a tuple of RGB values.
        save_path (str): The path to save the generated image.

    Returns:
        None
    """

    # Generate images
    for font_file in os.listdir(font_dir):

        if font_file.endswith(".ttf"):
            font_path = os.path.join(font_dir, font_file)
            font = ImageFont.truetype(font_path, random.choice(font_sizes))

            for char in characters:

                for bg_color in bg_colors:

                    for font_color in font_colors:

                        image = Image.new("RGB", (30, 30), bg_color)
                        draw = ImageDraw.Draw(image)

                        # Calculate the size of the text and the position to center it
                        text_size = draw.textsize(char, font=font)
                        text_x = (30 - text_size[0]) // 2
                        text_y = (30 - text_size[1]) // 2
                        draw.text((text_x, text_y), char, font=font, fill=font_color)                        
                        # file_name = f"{uuid.uuid4()}.png"
                        # image.save(os.path.join(save_path, file_name))
                        # save_img(save_path, image)
                        make_variation(image, char, save_path)

def main() -> None:
    # Define the path to save the generated images
    save_path = "../data/raw"

    # Set font directory path
    font_dir = "../fonts"

    # Set characters to generate
    characters = "ሀሁሂሃሄህሆለሉሊላሌልሎሏሐሑሒሓሔሕሖሗመሙሚማሜምሞሟሠሡሢሣሤሥሦሧረሩሪራሬርሮሯሰሱሲሳሴስሶሷሸሹሺሻሼሽሾሿቀቁቂቃቄቅቆቈቊቋቌቍበቡቢባቤብቦቧቨቩቪቫቬቭቮቯተቱቲታቴትቶቷቸቹቺቻቼችቾቿኀኁኂኃኄኅኆኈኊኋኌኍነኑኒናኔንኖኗኘኙኚኛኜኝኞኟአኡኢኣኤእኦኧከኩኪካኬክኮኰኲኳኴኵኸኹኺኻኼኽኾወዉዊዋዌውዎዐዑዒዓዔዕዖዘዙዚዛዜዝዞዟዠዡዢዣዤዥዦዧየዩዪያዬይዮደዱዲዳዴድዶዷጀጁጂጃጄጅጆጇገጉጊጋጌግጎጐጒጓጔጕጠጡጢጣጤጥጦጧጨጩጪጫጬጭጮጯጰጱጲጳጴጵጶጷጸጹጺጻጼጽጾጿፀፁፂፃፄፅፆፈፉፊፋፌፍፎፏፐፑፒፓፔፕፖፗ‐–,፡፣፤፥፦!?.።‹›«»()\\[]፧፨፠፩፪፫፬፭፮፯፰፱፲፳፴፵፶፷፸፹፺፻"
    # characters = "ሀ"

    # Set font sizes to use
    font_sizes = [12, 14, 16, 18, 20, 24, 36, 48]

    # Set background colors to use
    bg_colors = [(255, 255, 255), (200, 200, 200), (150, 150, 150)]

    # Set font colors to use
    font_colors = [(0, 0, 0), (50, 50, 50), (100, 100, 100)]

    # Create the save path if it doesn"t exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Define default values for all arguments
    default_args = {
        "save_path" : save_path,
        "font_dir" : font_dir,
        "characters" : characters,        
        "font_sizes" : font_sizes,
        "bg_colors" : bg_colors,
        "font_colors" : font_colors,
        "num_images": 1000
    }

    # Command line arguments
    parser = argparse.ArgumentParser(description="Generate OCR dataset using sets of fonts")
    
    parser.add_argument("--font-dir", type=str, required=False,
                        help="Directory containing fonts")
    parser.add_argument("--output-dir", type=str, required=False,
                        help="Directory to save generated images")
    parser.add_argument("--font-sizes", type=list, required=False,
                        help="Comma-separated list of font sizes to use")
    parser.add_argument("--bg-colors", type=list, required=False,
                        help="Comma-separated list of background colors to use, in the format (R,G,B)")
    parser.add_argument("--font-colors", type=list, required=False,
                        help="Comma-separated list of font colors to use, in the format (R,G,B)")
    parser.add_argument("--characters", type=str, required=False,
                        help="Comma-separated list of characters to generate")
    parser.add_argument("--num-images", type=int, required=False,
                        help="Number of images to generate for each font, size, and color combination")
    args = parser.parse_args()

    # Check for passed arguments
    if args.font_dir is None or args.output_dir is None or args.bg_colors is None or args.font_colors is None or args.characters is None:        

        # Update the default arguments with user-provided values
        for arg_name, arg_value in vars(args).items():
            if arg_value is not None:
                default_args[arg_name] = arg_value
        
        generate_img(
            default_args['characters'], 
            default_args['font_dir'], 
            default_args['font_sizes'], 
            default_args['bg_colors'], 
            default_args['font_colors'], 
            default_args['save_path']
            )        
    else:
        generate_img(
            default_args['characters'], 
            default_args['font_dir'], 
            default_args['font_sizes'], 
            default_args['bg_colors'], 
            default_args['font_colors'], 
            default_args['save_path']
            )        


if __name__ == "__main__":
    main()