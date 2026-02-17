from tqdm import tqdm

def progress_bar(total, desc):
    return tqdm(total=total, desc=desc, ncols=80)

