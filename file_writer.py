import csv


def write_to_file(data):
    with open('database.txt', mode='a') as database_01:
        for item in data:
            database_01.write(f"{str(item.capitalize())} - {str(data[item])} \n")
        database_01.write("\n")


def write_to_csv(data):
    with open('database.csv', newline='', mode='a') as database_02:
        headers = data.keys()
        database_02_writer = csv.DictWriter(database_02, fieldnames=headers)
        # to ensure that the headers is written only once and not everytime when the file is written.
        # it will be at 0 only if it's a new file.
        if database_02.tell() == 0:
            database_02_writer.writeheader()
        database_02_writer.writerow(data)
