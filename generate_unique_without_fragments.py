#Find all # that in urls in url.txt
def url_without_fragment(url):
    sign = url.find("#")
    if sign == -1:
        return url
    return url[: sign]

#delete all # in the urls.txt
def read_delete_fragment(path="urls.txt"):
    result = set()
    with open(path, "r") as fr:
        for url in fr.readlines():
            url_no_fragment = url_without_fragment(url)
            result.add(url_no_fragment)
    with open("url_no_fragments.txt", "w") as fw:
        out = []
        for url in result:
            out.append(url)
        fw.writelines(out)
    print(f"Number of unique urls is {len(out)}")


if __name__ == '__main__':
    read_delete_fragment()