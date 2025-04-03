import os
import re
from datetime import datetime, timedelta

def rename_files():
    folder = os.path.join(os.getcwd(), "ChangeFiles")
    pattern = re.compile(r'(\d{8}_\d{6})')

    for filename in os.listdir(folder):
        match = pattern.search(filename)
        if match:
            name_part = match.group(1)
            ext = os.path.splitext(filename)[1]
            old_path = os.path.join(folder, filename)
            new_name = name_part + ext
            new_path = os.path.join(folder, new_name)

            while os.path.exists(new_path):
                dt = datetime.strptime(name_part, "%Y%m%d_%H%M%S")
                dt += timedelta(seconds=1)
                name_part = dt.strftime("%Y%m%d_%H%M%S")
                new_name = name_part + ext
                new_path = os.path.join(folder, new_name)

            os.rename(old_path, new_path)

if __name__ == "__main__":
    rename_files()