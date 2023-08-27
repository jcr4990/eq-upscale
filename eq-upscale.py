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
args = parser.parse_args()

if os.path.exists("archives") is False:
    os.mkdir("archives")

if os.path.exists("extracted") is False:
    os.mkdir("extracted")

archives = os.listdir("archives")
archive_found = False
for archive in archives:
    # Extract s3d/eqg
    if archive.endswith(".s3d") or archive.endswith(".eqg"):
        archive_found = True
        result = subprocess.run(["quail", "extract", "archives//" + archive, "extracted//_" + archive], shell=True, capture_output=True, text=True,)
        print(result.stdout)

        # Iterate files in archive folder and upscale with realesrgan
        files = os.listdir("extracted//_" + archive)
        files_to_process = 0
        files_processed = 0
        for file in files:
            if (file.endswith(".dds") or file.endswith(".bmp") or file.endswith(".png")) and file.startswith(tuple(args.texture_prefix.split(","))):
                files_to_process += 1

        if len(args.texture_prefix) > 0:
            print(f"{archive} contains {files_to_process} images to process. (filtered by prefix: {args.texture_prefix})\n")
        else:
            print(f"{archive} contains {files_to_process} images to process.\n")

        for file in files:
            if (file.endswith(".dds") or file.endswith(".bmp") or file.endswith(".png")) and file.startswith(tuple(args.texture_prefix.split(","))):
                files_processed += 1
                original_path = "extracted//_" + archive + "//" + file
                upscaled_path = "tmp//" + file.split(".")[0] + ".png"
                img_format = get_format(original_path)

                if img_format == "bmp":
                    if transparency_check(original_path) is True:
                        print(f"Skipping texture with transparency: {file}")
                        print(f"Progress: {files_processed}/{files_to_process}\n")
                        continue

                print(f"File: {file}\nType: {img_format}")
                result = subprocess.run(["realesrgan-ncnn-vulkan.exe", "-i", original_path, "-o", upscaled_path, "-n", "realesrgan-x4plus", "-s", args.scale], shell=True, capture_output=True, text=True,)

                save_upscaled_img(img_format, original_path, upscaled_path)
                print(f"Progress: {files_processed}/{files_to_process}\n")

        # Compress upscaled images back into archive
        result = subprocess.run(["quail", "compress", "extracted//_" + archive], shell=True, capture_output=True, text=True,)

if archive_found is False:
    print("No .eqg or .s3d files found in /archives")
