#def sort_by_ip (filename):
#    with open(filename, 'r') as file:
#        lines = file.readlines()
#    
#    for line in lines :
#        ip = line.split(' #')[0].split(',')[2].split('.')[0:4]
#        print(ip)
#
#sort_by_ip("output.txt")

def sort_file_by_ip(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Extract IP from each line and convert it to tuple for correct sorting
    lines.sort(key=lambda line: tuple(map(int, line.split(' #')[0].split(',')[2].split('.')[0:4])))

    with open('sorted_output.txt', 'w') as file:
        for line in lines:
            file.write(line)

sort_file_by_ip('output.txt')
