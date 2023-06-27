import logging as lg

from anyio import Path, run_process

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.utils.filesystem import rmtree


logger = lg.getLogger(__name__)


async def compress_final_proceedings(final_proceedings: ProceedingsData, cookies: dict, settings: dict):
    """ """

    site_preview_ctx = f'{final_proceedings.event.id}'
    site_preview_dir = Path(site_preview_ctx)
    site_preview_zip = Path(f"{site_preview_ctx}.7z")
    working_dir = Path('var', 'html')
    
    zip_cmd = await Path('bin', '7zzs').absolute()
    
    full_dest_path = await Path(working_dir, f"{site_preview_ctx}.7z").absolute()
    if await full_dest_path.exists():
        await full_dest_path.unlink()

    zip_args = [f"{zip_cmd}", "a",
                "-t7z", "-m0=Deflate",
                "-ms=16m", "-mmt=4", 
                "-bd", "-mx=1", "--",
                f"{site_preview_zip}",
                f"{site_preview_dir}"]

    logger.info(" ".join(zip_args))

    result = await run_process(zip_args, cwd=str(working_dir))

    if result.returncode == 0:
        logger.info(result.stdout.decode())
    else:
        logger.info(result.stderr.decode())


# ######### OK 7Z LZ4
# # zip_args = [f"bin/p7zip/7z", "a", "-m0=lz4", 
# #             "-mx=1", "-mmt=4", "-bd", "--", 
# #             f"{zip_file_path}", f"{out_dir_path}"]
# 
# # bin/p7zip/7z a -m0=lz4 -mx=1 -mmt=4 -bd -- out.7z var/run/21_src/out
# 
# """ LZMA2 """
# 
# # -t7z sets the archive type to 7-Zip.
# # -m0=LZMA2:d64k:fb32 defines the usage of LZMA2 compression method with a dictionary size of 64 KB and a word size (fast bytes) of 32.
# # -ms=8m enables solid mode with a solid block size of 8 MB.
# # -mmt=30 enables multi-threading mode with up to 30 threads.
# # -mx=1 selects fastest compressing as level of compression.
# 
# # zip_args = [f"{zip_cmd}", "a",
# #             "-t7z", "-m0=LZMA2:d64k:fb32",
# #             "-ms=16m", "-mmt=4", "-mx=1", "--",
# #             f"{zip_file_path}", f"{out_dir_path}"]        
# 
# """ Deflate """
# 
# # ./bin/7zzs a -t7z -m0=deflate -mx=1 -mmt=4 var/html/fel2022.7z var/html/fel2022
# 
# zip_args = [f"{zip_cmd}", "a",
#     "-t7z", "-m0=Deflate",
#     "-ms=16m", "-mmt=4", "-mx=1", "--",
#     f"{zip_file_path}", f"{out_dir_path}"]
# 
# """ LZMA """
# 
# # 7z a -t7z -m0=lzma -mx=1 -mfb=64 -md=32m -ms=on
# 
# #zip_args = [f"{zip_cmd}", "a",
# #    "-t7z", "-m0=LZMA", "-mx=1", "-ms=on",
# #    "-mfb=64", "-md=32m", "-mmt=2",  "--",
# #    f"{zip_file_path}", f"{out_dir_path}"]
# 
# """ """