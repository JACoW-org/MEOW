from anyio import Path


async def clean_final_proceedings(event: dict, cookies: dict, settings: dict):
    
    working_dir = Path(f"/tmp/{event.get('id')}")
    
    await working_dir.mkdir(parents=True, exist_ok=True)

    print('temporary directory', await working_dir.absolute())
    
    # await working_dir.rmdir()
    
    