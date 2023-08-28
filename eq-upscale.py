import argparse
import os
import subprocess
from PIL import Image


def get_format(path):
    with open(path, 'rb') as file:
        header = file.read(4)

        if header == b'DDS ':
            return "dds"
        elif header == b'\x89PNG':
            return "png"
        elif header[:2] == b'BM':
            return "bmp"
        else:
            print(header)
            print("Unknown File Format?")


def save_upscaled_img(img_format, original_path, upscaled_path):
    img = Image.open(upscaled_path)

    if os.path.exists(original_path):
        os.remove(original_path)

    img.save(original_path + "." + img_format)
    os.rename(original_path + "." + img_format, original_path)


def transparency_check(path):
    bmp = Image.open(path)
    bmp_palette = bmp.getpalette()
    try:
        transparent_rgb = bmp_palette[0:3]
    except TypeError:
        return False

    if transparent_rgb[0] > 240 and transparent_rgb[1] < 15 and transparent_rgb[2] > 240:
        return True
    else:
        return False


# Init
msg = "Welcome to eq-upscale. Use this tool to upscale texture images located inside .eqg/.s3d EverQuest archive files."
parser = argparse.ArgumentParser(description=msg)
parser.add_argument("-s", "--scale", help="Upscale ratio (can be 2, 3, 4. default=4)", default="4", type=str)
parser.add_argument("-t", "--texture_prefix", help="Comma separated texture prefix filter. Only upscale textures starting with these values. For example -t stone,rock will upscale all textures starting with 'stone' or 'rock'", default="", type=str)
parser.add_argument("-m", "--model", help="Models included: realesrgan-x4plus, realesrgan-x4plus-anime, realesr-animevideov3-x2, realesr-animevideov3-x3, realesr-animevideov3-x4 (default=realesrgan-x4plus)", default="realesrgan-x4plus", type=str)
parser.add_argument("-a", "--archive", help="Specify an archive in the 'archives' folder to target. Can select multiple separated by comma. For example: qeynos2.s3d,everfrost.s3d (default will target every archive in folder)", default=None, type=str)
args = parser.parse_args()

if args.archive is None:
    archives = os.listdir("archives")
else:
    archives = args.archive.split(",")

archive_found = False
for archive in archives:
    # Extract eqg/s3d
    if archive.endswith(".s3d") or archive.endswith(".eqg"):
        archive_found = True
        textures_to_process = []
        textures_processed = 0
        result = subprocess.run(["quail", "extract", "archives//" + archive, "extracted//_" + archive], shell=True, capture_output=True, text=True,)
        print(result.stdout)

        # Iterate files in archive and append textures to be processed to list
        for file in os.listdir("extracted//_" + archive):
            if (file.endswith(".dds") or file.endswith(".bmp") or file.endswith(".png")) and file.startswith(tuple(args.texture_prefix.split(","))):
                textures_to_process.append(file)

        if len(args.texture_prefix) > 0:
            print(f"{archive} contains {len(textures_to_process)} images to process. (filtered by prefix: {args.texture_prefix})\n")
        else:
            print(f"{archive} contains {len(textures_to_process)} images to process.\n")

        # Iterate textures to be processed with realesrgan
        for file in textures_to_process:
            original_path = "extracted//_" + archive + "//" + file
            upscaled_path = "tmp//" + file.split(".")[0] + ".png"
            img_format = get_format(original_path)

            if img_format == "bmp":
                if transparency_check(original_path) is True:
                    textures_processed += 1
                    print(f"Skipping texture with transparency: {file}")
                    print(f"Progress: {textures_processed}/{len(textures_to_process)}\n")
                    continue

            print(f"File: {file}\nType: {img_format}")
            result = subprocess.run(["realesrgan-ncnn-vulkan.exe", "-i", original_path, "-o", upscaled_path, "-n", args.model, "-s", args.scale], shell=True, capture_output=True, text=True,)
            save_upscaled_img(img_format, original_path, upscaled_path)
            textures_processed += 1
            print(f"Progress: {textures_processed}/{len(textures_to_process)}\n")

        # Compress upscaled images back into archive
        result = subprocess.run(["quail", "compress", "extracted//_" + archive], shell=True, capture_output=True, text=True,)

# tmp files cleanup
for file in os.listdir("tmp"):
    os.remove("tmp//" + file)

if archive_found is False:
    print("No .eqg or .s3d files found in /archives")
