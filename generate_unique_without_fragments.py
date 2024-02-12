#Find all # that in urls in url.txt
def url_without_fragment(url):
    sign = url.find("#") # find the index of #
    if sign == -1: # if the return value is -1 it means no #
        return url
    return url[: sign] # return the slice of url from 0 to sign

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

# Function for reading from logs
def create_unique_urls_file():
    path = "Logs/PotentiallyFinalWorker.log"
    result = set()
    with open(path, "r", encoding="utf-8") as fr:
        for line in fr:
            first_i = line.find("h")
            line = line[first_i:]
            end_i = line.find(",")
            url = line[: end_i]
            url_no_fragment = url_without_fragment(url)
            result.add(url_no_fragment)
    
    with open("deliverable_question_1.txt", 'w') as fw:
        for url in result:
            fw.write(url + '\n')

    print(f"Number of unique urls is {len(result)}")

if __name__ == '__main__':
    create_unique_urls_file()