import math


def tokenize(content):
    # Split the content into words
    return content.lower().split()

def count_words(tokens):
    # Count the frequency of each word
    word_count = {}
    for word in tokens:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count


def compute_dot_product(count1, count2):
    # Compute the dot product of two frequency vectors
    dot_product = 0
    for word in count1:
        if word in count2:
            dot_product += count1[word] * count2[word]
    return dot_product


def compute_magnitude(count):
    # Compute the magnitude (Euclidean norm) of a frequency vector
    magnitude = 0
    for word in count:
        magnitude += count[word] ** 2
    return math.sqrt(magnitude)


def compute_cosine_similarity(content1, content2):
    tokens1 = tokenize(content1)
    tokens2 = tokenize(content2)

    count1 = count_words(tokens1)
    count2 = count_words(tokens2)

    dot_product = compute_dot_product(count1, count2)
    magnitude1 = compute_magnitude(count1)
    magnitude2 = compute_magnitude(count2)

    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    cosine_sim = dot_product / (magnitude1 * magnitude2)
    return cosine_sim

if __name__ == '__main__':
    content1 = "This is the first piece of content."
    content2 = "This is the second piece of content."
    cosine_sim = compute_cosine_similarity(content1, content2)
    print("Cosine Similarity:", cosine_sim)
