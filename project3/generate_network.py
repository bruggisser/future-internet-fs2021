# 40 satelites per orbit
# 40 orbits
links = []
for i in range(0, 40):
    for j in range(0, 40):
        k = j + i*40
        l = k + 1 if j < 39 else i * 40
        link = (k, l)
        links.append(link)

for i in range(0, 40):
    for j in range(0, 40):
        k = i + 40 * j
        l = i + 40 + (40 * j) if j < 39 else (i + 40 + (40 * j)) % 40
        link = (k, l)
        links.append(link)


with open("./output_data/links.txt", "w") as f:
    for link in links:
        f.write("{},{}\n".format(link[0], link[1]))
