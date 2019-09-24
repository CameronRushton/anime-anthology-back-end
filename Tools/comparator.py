import sys
import difflib

# print(str(sys.argv))

# Threshold is the value of how close levenshtein can come to matching the strings exactly for the strings to be considered a match.
# For example, setting a threshold of 0 means that the strings must be exact to match. Threshold of 7 means that while looking at the string, if it's ever 7 degrees (steps) from matching the other string, we will consider it more to be a match candidate.
def compare(string1, string2, threshold):
    lev_matrix = levenshtein(string1, string2)
    lev_dist = lev_matrix[len(string2)]
    is_subset = False

    if lev_dist == 0:
        print("%s and %s are the same.", string1, string2)
        return
    elif lev_dist <= threshold:
        print(string1, " and ", string2, " are within the threshold; They might be the same show, but different season.")

    if 0 in lev_matrix:
        # At some point, we matched the two strings, so one string is a subset of the other string; It is highly likely that these shows are the same show, though not 100% because a show called 'k' exists.
        is_subset = True

    # Did we match a lot of the characters? Did we match a lot of the bigger words (many consecutive decreases in a row)?
    # word_match_score = word_match(lev_matrix)  # High number is better, negative means to not count it as something went wrong.
    print(lev_matrix)
    # print("word match score is ", word_match_score)


# def word_match(lev_matrix):
#     if len(lev_matrix) < 3:
#         print("Not counting word_match in the calculation because lev_matrix is too small: " + str(lev_matrix))
#         return -1
#
#     word_scores = []
#     word_score = 0
#     for i in range(0, len(lev_matrix) - 1):
#         curr = lev_matrix[i + 1]
#         prev = lev_matrix[i]
#         if curr < prev:
#             word_score += 1
#         elif curr >= prev:
#             if word_score > 3:  # Make this threshold higher if we only want to include big word matches. Matching a single 5 character word is more indicative than matching 5 random letters.
#                 word_scores.append(word_score)
#             word_score = 0
#
#     word_scores.append(word_score)
#     matrix_size = len(lev_matrix)
#     total_score = 0
#     for score in word_scores:
#         # Normalize - we're subtracting 1 because the score is based on the count *between* the values of which there are length-1 'between' hops.
#         score = score/(matrix_size - 1)
#         total_score += score
#     return total_score * 100

# The final value from levenshtein will be the number of mutations necessary
# (counting replaces as an operation, i.e. a deletion followed by an addition in the same place does not count as two operations)
# to mutate one string to another.
def levenshtein(s, t):
    # From Wikipedia article; Iterative with two matrix rows.
    if s == t:
        return 0
    elif len(s) == 0:
        return len(t)
    elif len(t) == 0:
        return len(s)
    v0 = [None] * (len(t) + 1)
    v1 = [None] * (len(t) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]

    return v1



cases=[('kizumonogatari', 'owarimonogatari'),
       ('highschool-of-the-dead', 'highschool-dxd'),
       ('highschool-dxd', 'wasteful-days-of-highschool-girl'),
       ('k', 'k:return-of-kings')]
#
for a, b in cases:
    compare(a, b, 7)
    seq = difflib.SequenceMatcher(None, a, b)
    d = seq.ratio()*100
    print("Sequence match: ", d)
    print('{} => {}'.format(a, b))
    for i,s in enumerate(difflib.ndiff(a, b)):
        if s[0]==' ': continue
        elif s[0]=='-':
            print(u'Delete "{}" from position {}'.format(s[-1], i))
        elif s[0]=='+':
            print(u'Add "{}" to position {}'.format(s[-1], i))
    print()



# If v1 has a min value in the array of 7 - 0 (I need a big known sample size to do some tweaking for this value), then we can assume it's the same show, different season. See the monogatari series.

# highschool-of-the-dead and highschool-dxd will be an issue with the methods below. We need to look for signs of the words 'season' or 'part' as well?.


#disance is 33 for hunter-x-hunter and hunter-x-hunter-23456789111315171921232527293133 & v1=[15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33] - there was a point when it got '0' which is an exact match then it wasnt a match for 33 more chars
# ...if the alg removed a number of characters from one string but didnt add many (or any at all - then this would be obviously another season), then it's probably another season.

# Something else I can do is split the string by the hyphen and compare each word. If we get any matches, the shows are likely to be related. If we get two matches, then it's almost guaranteed. If theres 3 or more, I'd almost be certain.
# ... Problems: The word 'highschool' and filler words like 'no', 'wa', 'ga', 'and', 'the', 'a', 'of', 'not', 'nai', etc... Options: Filter these words or the word must be >= 5 chars.

# TODO: Look for words like 'season' and markers like the colon for the root show name.