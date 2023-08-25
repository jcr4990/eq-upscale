# eq-upscale

Experimental tool for AI upscaling various textures within EverQuest .eqg and .s3d archive files.

## Installation

Simply clone this repo (or download zip) and place desired .s3d or .eqg file in the "archives" folder. Then open a terminal/command prompt and type the following:
```
python eq-upscale.py
```
This will upscale every texture file within any archive file located in the "archives" folder. Once complete a new version of each .eqg/.s3d archive will be generated in the root eq-upscale folder. Simply copy this archive into your EverQuest directory and overwrite the existing one to load them into the game. Be sure to make backup copies of your original archive files just in case.

## Arguments

To specify only specific texture files you may use the -t argument followed by a comma separated list of file name prefixes.
For example say you have an archive file named zone.eqg and within zone.eqg are many various texture files but you specifically want the ones beginning with "grass" and "stone". You would instead type:
```
python eq-upscale.py -t grass,stone
```
eq-upscale will ignore any textures that don't begin with "grass" or "stone". You can use this to selectively upscale specific textures. Depending on which version of EverQuest you intend to play. You may be limited to a 32 bit client and thus will need to be cautious about being too extensive with upscaling or risk client crashes due to lack of memory.

eq-upscale will upscale all textures by 4x by default. If you wish you can select 2x or 3x instead with the -s argument like so:
```
python eq-upscale.py -s 2
```

## External Resources
This project would not be possible without the extensive work of the developer(s) of both "Quail" and "Real-ESRGAN-ncnn-vulkan"

https://github.com/xackery/quail

https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan
<br/><br/><br/><br/>

> [!WARNING]
> You are likely to encounter some bugs. I've spent many hours fiddling with EQ files and I've learned there's always bound to be surprises. Make sure you back up your original files in case something goes haywire.