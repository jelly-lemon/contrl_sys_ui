import csv
import os

import util

if __name__ == '__main__':
    # 追加数据到末尾
    file_dir = "./other/test"
    file_name = "test.csv"
    file_path = file_dir + "/" + file_name
    if os.path.exists(file_dir) is False:
        os.makedirs(file_dir)
        file = open(file_path, mode="w", encoding="utf-8", newline='')
    else:
        file = open(file_path, mode="a", encoding="utf-8", newline='')

    csv_writer = csv.writer(file, dialect='excel')

    data_row = util.get_time()
    csv_writer.writerow(['time', data_row])
    data_row = util.get_time()
    csv_writer.writerow(['time', data_row])

    file.close()