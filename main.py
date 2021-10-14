import zipfile
import hashlib
import requests
import re
import os
import csv

directory_to_extract_to = 'test_dir'     # директория извлечения файлов архива
arch_file = 'tiff-4.2.0_lab1.zip'  # путь к архиву
os.mkdir(directory_to_extract_to)
archive = zipfile.ZipFile(arch_file, 'r')
archive.extractall(directory_to_extract_to)
archive.close()


txt_files = []
txt_files2 = []
for root, dirs, files in os.walk(directory_to_extract_to):
    for file in files:
        if file.endswith(".txt"):
            path = os.getcwd()+'\\'+root + "\\" + file
            txt_files.append(path)
print(txt_files)

for file in txt_files:
    file_data = open(file, 'rb').read()
    result = hashlib.md5(file_data).hexdigest()
    print(result)

for root, dirs, files in os.walk(directory_to_extract_to):
    for file in files:
        path = os.getcwd() + '\\' + root + "\\" + file
        txt_files2.append(path)
target_hash = "4636f9ae9fef12ebd56cd39586d33cfb"
for file in txt_files2:
    file_data1 = open(file, 'rb').read()
    result = hashlib.md5(file_data1).hexdigest()
    if result == target_hash:
        target_file = file
        print(target_file)
with open(target_file, "r") as f:
    target_file_data = f.read()
    print(target_file_data)
    f.close()


r = requests.get(target_file_data)
result_dct = {}  # словарь для записи содержимого таблицы

counter = 0
headers = []
# Получение списка строк таблицы
lines = re.findall(r'<div class="Table-module_row__3TH83">.*?</div>.*?</div>.*?</div>.*?</div>.*?</div>', r.text)
for line in lines:
    heads = (re.findall(
        r'<div class="Table-module_cell__EFKDW Table-module_header__1exlo Table-module_gray__3da6S.*?</div>',
        line
    ))
    if counter == 0:
        for head in heads:
            headers.append(re.sub(r'<[^>]*>', '', head))
            counter += 1
        continue
    temp = re.sub(r'<[^>]*>', ';', line)
    temp = re.sub(r';[(].*?[)];', '', temp)
    temp = re.sub(r';;*', ';', temp)
    temp = temp[1:len(temp)-1]
    tmp_split = temp.split(";")
    country_name = tmp_split[0]
    country_name = re.search(r"[а-яА-ЯёЁ -«»]+", country_name).group(0).strip()

    result_dct[country_name] = []
    for i in range(4):
        col_val = re.sub(r'\xa0', '', tmp_split[i+1])
        col_val = re.sub(r'_', '-1', col_val)
        col_val = re.sub(r'0[*]', '0', col_val)
        result_dct[country_name].append(col_val)
    counter += 1

with open('data.csv', 'w') as output:
    writer = csv.DictWriter(output, fieldnames=headers, delimiter=';')
    writer.writeheader()
    for key in result_dct:
        writer.writerows([{
            headers[0]: key,
            headers[1]: result_dct[key][0],
            headers[2]: result_dct[key][1],
            headers[3]: result_dct[key][2],
            headers[4]: result_dct[key][3]
        }])

target_country = input("Введите название страны: ")
count = 0
j = 1
with open('data.csv', "r") as file:
    reader = csv.reader(file)
    for row in reader:
        if count == 0:
            heads = row[0].split(";")
            count += 1
        if row:
            tmp = row[0].split(";")
            if tmp[0] == target_country:
                for i in tmp[1:len(tmp)]:
                    print(heads[j], ":", i)
                    j += 1
