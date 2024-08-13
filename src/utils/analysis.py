def one_letter_away_words(word: str, word_list: list[str], checked_shapes: set[tuple[int, str]]) -> list[list[str]]:
    groups = []
    for i in range(len(word)):
        shape = word[:i] + word[i + 1 :]
        if (i, shape) in checked_shapes:
            continue
        checked_shapes.add((i, shape))
        groups.append([w for w in word_list if shape == w[:i] + w[i + 1 :] and w[i] not in shape])
    return groups


def remove_capitalized_duplicates(word_list: list[str]) -> list[str]:
    found = set()
    result = []
    for word in word_list:
        if word.lower() not in found:
            found.add(word.lower())
            result.append(word)
    return result


def largest_1_letter_away_group(word_list: list[str]) -> list[str]:
    largest = []
    alternatives = []
    checked_shapes = set()
    word_list = remove_capitalized_duplicates(word_list)
    for word in word_list:
        groups = one_letter_away_words(word, word_list, checked_shapes)
        if not groups:
            continue
        largest_new = max(groups, key=len)
        if len(largest_new) > len(largest):
            largest = largest_new
            alternatives = []
        elif len(largest_new) == len(largest):
            alternatives.append(largest_new)
    if alternatives:
        print(f"Found alternative groups of size {len(largest)} for {largest}: {alternatives}")
    return largest
