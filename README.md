> [!WARNING]
> There are likely bugs I've yet to encounter. Always back up your original files first to be safe.
# eq-upscale
Experimental tool for AI upscaling various textures within EverQuest .eqg and .s3d archive files.
## Installation & Usage
Assuming Python is already installed. Clone this repo (or download zip and extract then open a command prompt) and cd to the eq-upscale folder. The only dependency needed is Pillow image library which can be installed by typing "pip install -r requirements.txt". From that point you should be all set. Head on over to your EQ folder and grab your desired .s3d or .eqg file(s) and place them in the "archives" subfolder of eq-upscale. Then in your command prompt window type the following:
```
python eq-upscale.py
```
This will upscale every texture file within any archive file located in the "archives" folder. Once complete a new version of each .eqg/.s3d archive will be generated in the root eq-upscale folder. Simply copy this archive into your EverQuest directory and overwrite the existing one to load them into the game (client restart required). Depending which version of EQ you intend to play you may be limited to a 32bit client and thus will need to be selective in which textures you choose to upscale. You will likely face client crashes if you try to upscale a very large number of textures. You may customize your settings with optional arguments listed below.

### Select Specific Archives
To specify only specific archive file(s) you may use the -a argument followed by an archive name or multiple archives separated by comma.

Example:
```
python eq-upscale.py -a global_chr.s3d,global4_chr.s3d
```
Any archive files in your 'archives' folder not specified when using the -a argument will be ignored.

### Select Specific Textures
To specify only specific texture files you may use the -t argument followed by a comma separated list of file name prefixes. Say you have an archive file named zone.eqg and within zone.eqg are many various texture files but you specifically want the ones beginning with "grass" and "stone"

Example:
```
python eq-upscale.py -t grass,stone
```
eq-upscale will ignore any textures that don't begin with "grass" or "stone". You can use this to selectively upscale specific textures.

### Select Scale
eq-upscale will upscale all textures by 4x by default. If you wish you can select 2x or 3x instead with the -s argument.

Example:
```
python eq-upscale.py -s 2
```
2x and 3x scaling have not been extensively tested yet to work properly once in-game. In most cases you wouldn't need to use this option. Primarily added it as an option if memory becomes an issue and starts causing client crashes. Bringing down the scale may help in this case.

### Select Model
realesrgan-ncnn-vulkan comes packaged with five pre-trained models for upscaling. You can select your model with the -m argument. The options are: realesrgan-x4plus, realesrgan-x4plus-anime, realesr-animevideov3-x2, realesr-animevideov3-x3, realesr-animevideov3-x4

Example:
```
python eq-upscale.py -m realesrgan-x4plus-anime
```
I have personally only tested realesrgan-x4plus and realesrgan-x4plus-anime and both work fine in my testing.

## External Resources
This project would not be possible without the extensive work of the developer(s) of both "Quail" and "Real-ESRGAN-ncnn-vulkan"

https://github.com/xackery/quail

https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan
