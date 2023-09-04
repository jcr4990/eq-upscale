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


def save_upscaled_img(img_format, original_path, upscaled_path, bmp_index):
    img = Image.open(upscaled_path)

    if os.path.exists(original_path):
        os.remove(original_path)

    if bmp_index:
        img.save(original_path + ".png")
        os.rename(original_path + ".png", original_path)
    else:
        img.save(original_path + "." + img_format)
        os.rename(original_path + "." + img_format, original_path)


def check_bmp_index(path):
    bmp = Image.open(path)
    bmp_palette = bmp.getpalette()
    try:
        palette = bmp_palette[0:3]
    except TypeError:
        return False

    return True


def mod_bmp(original_path):
    bmp = Image.open(original_path)
    bmp_palette = bmp.getpalette()
    rgb_to_alpha = bmp_palette[0:3]
    bmp = bmp.convert("RGBA")
    pixeldata = list(bmp.getdata())

    for i, pixel in enumerate(pixeldata):
        if pixel[:3] == tuple(rgb_to_alpha):
            pixeldata[i] = (rgb_to_alpha[0], rgb_to_alpha[1], rgb_to_alpha[2], 0)

    bmp.putdata(pixeldata)
    png_path = original_path.replace(".bmp", ".png")
    bmp.save(png_path)

    if os.path.exists(original_path):
        os.remove(original_path)

    os.rename(png_path, original_path)


def fix_bleed(upscaled_path):
    img = Image.open(upscaled_path)
    if img.mode == "RGBA":
        modded_img = img.copy()
        modded_img = modded_img.transpose(Image.FLIP_TOP_BOTTOM)
        pixel_data = modded_img.load()

        for x in range(modded_img.width):
            for y in range(modded_img.height):
                r, g, b, a = pixel_data[x, y]

                if a < 250 and a > 0:
                    pixel_data[x, y] = (r, g, b, 0)

        modded_img.save(upscaled_path)


# Init
msg = "Welcome to eq-upscale. Use this tool to upscale texture images located inside .eqg/.s3d EverQuest archive files."
parser = argparse.ArgumentParser(description=msg)
parser.add_argument("-s", "--scale", help="Upscale ratio (can be 2, 3, 4. default=4)", default="4", type=str)
parser.add_argument("-t", "--texture_prefix", help="Comma separated texture prefix filter. Only upscale textures starting with these values. For example -t stone,rock will upscale all textures starting with 'stone' or 'rock'", default="", type=str)
parser.add_argument("-m", "--model", help="Models included: realesrgan-x4plus, realesrgan-x4plus-anime, realesr-animevideov3-x2, realesr-animevideov3-x3, realesr-animevideov3-x4 (default=realesrgan-x4plus)", default="realesrgan-x4plus", type=str)
parser.add_argument("-a", "--archive", help="Specify an archive in the 'archives' folder to target. Can select multiple separated by comma. For example: qeynos2.s3d,everfrost.s3d (default will target every archive in folder)", default=None, type=str)
parser.add_argument("-f", "--fix_alpha", action="store_true", help="Use this flag if you encounter textures that are supposed to be transparent but don't display properly after upscaling. Will slow down the upscaling process a bit. Recommended to only use on specific textures that have transparency issues.")
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

            if args.fix_alpha and img_format == "bmp":
                bmp_index = check_bmp_index(original_path)
                if bmp_index:
                    mod_bmp(original_path)
            else:
                bmp_index = False

            print(f"File: {file}\nType: {img_format}")
            result = subprocess.run(["realesrgan-ncnn-vulkan.exe", "-i", original_path, "-o", upscaled_path, "-n", args.model, "-s", args.scale], shell=True, capture_output=True, text=True,)

            if result.stderr[-7:-1] == "failed":
                print(f"Decode image failed ({file}) skipping...")
                continue

            if args.fix_alpha and bmp_index:
                fix_bleed(upscaled_path)

            save_upscaled_img(img_format, original_path, upscaled_path, bmp_index)
            textures_processed += 1
            print(f"\nProgress: {textures_processed}/{len(textures_to_process)}\n")

        # Compress upscaled images back into archive
        result = subprocess.run(["quail", "compress", "extracted//_" + archive], shell=True, capture_output=True, text=True,)

# tmp files cleanup
for file in os.listdir("tmp"):
    os.remove("tmp//" + file)

if archive_found is False:
    print("No .eqg or .s3d files found in /archives")
