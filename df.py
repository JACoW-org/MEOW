import shutil

def get_disk_space():
    total, used, free = shutil.disk_usage("/")
    gb = lambda x: round(x / (1024**3), 2)
    return {"total_gb": gb(total), "used_gb": gb(used), "free_gb": gb(free)}

if __name__ == "__main__":
    df = get_disk_space()
    print(df)