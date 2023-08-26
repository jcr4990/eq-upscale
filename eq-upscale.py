import argparse
import os
import subprocess
from PIL import Image


def check_file_format(path):
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
            input("Unknown File Format?")


def handle_upscaled_png(img_format, original_path, upscaled_path):
    img = Image.open(upscaled_path)
    img = img.convert("RGBA")

    if os.path.exists(original_path):
        os.remove(original_path)

    img.save(original_path + "." + img_format)
    os.rename(original_path + "." + img_format, original_path)


# Init Parser
msg = "Welcome to eq-upscale. Use this tool to upscale texture images located inside .eqg/.s3d EverQuest archive files."
parser = argparse.ArgumentParser(description=msg)
parser.add_argument("-s", "--scale", help="Upscale ratio (can be 2, 3, 4. default=4)", default="4", type=str)
parser.add_argument("-t", "--texture_prefix", help="List of comma separated strings. Only upscale textures starting with these values.", default="", type=str)
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
        files_iterated = 0
        for file in files:
            if (file.endswith(".dds") or file.endswith(".bmp") or file.endswith(".png")) and file.startswith(tuple(args.texture_prefix.split(","))):
                original_path = "extracted//_" + archive + "//" + file
                upscaled_path = "tmp//" + file.split(".")[0] + ".png"
                img_format = check_file_format(original_path)

                print(f"File: {file}\nType: {img_format}")
                result = subprocess.run(["realesrgan-ncnn-vulkan.exe", "-i", original_path, "-o", upscaled_path, "-n", "realesrgan-x4plus", "-s", args.scale], shell=True, capture_output=True, text=True,)
                # print(result.stderr)

                handle_upscaled_png(img_format, original_path, upscaled_path)

                files_iterated += 1
                print(f"Completed File: {files_iterated}/{len(files)}\n")

        # Compress upscaled images back into archive
        result = subprocess.run(["quail", "compress", "extracted//_" + archive], shell=True, capture_output=True, text=True,)

if archive_found is False:
    print("No valid eqg or s3d archive files found")
