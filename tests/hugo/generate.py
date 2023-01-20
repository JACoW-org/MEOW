import time
import ulid

from anyio import run_process, Path


async def main():
    
    start = time.time()
    
    uuid = f"{ulid.ULID()}"
    
    print(uuid)
    
    site_path = await Path('var', 'run', uuid).absolute()
    
    hugo_cmd = await Path('bin', 'hugo').absolute()
    
    result = await run_process([f"{hugo_cmd}", "new", "site", f"{site_path}"])
    
    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(result.stderr.decode())
    
    end = time.time()
    
    print(end - start)
    