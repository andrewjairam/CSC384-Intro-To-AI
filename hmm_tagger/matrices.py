import numpy as np

# Table initialization
# initProbs dict
    # keys are POS tags
    # values are number of times POS is the tag in the first word in a sentence
    # numSentences key -> value = total number of sentences
initProbs = {'numSentences' : 0}
transProbs = {}
obsProbs = {}

# tags array: 91 total tags
TAGS = ["AJ0", "AJC", "AJS", "AT0", "AV0", "AVP", "AVQ", "CJC", "CJS", "CJT", "CRD",
        "DPS", "DT0", "DTQ", "EX0", "ITJ", "NN0", "NN1", "NN2", "NP0", "ORD", "PNI",
        "PNP", "PNQ", "PNX", "POS", "PRF", "PRP", "PUL", "PUN", "PUQ", "PUR", "TO0",
        "UNC", 'VBB', 'VBD', 'VBG', 'VBI', 'VBN', 'VBZ', 'VDB', 'VDD', 'VDG', 'VDI',
        'VDN', 'VDZ', 'VHB', 'VHD', 'VHG', 'VHI', 'VHN', 'VHZ', 'VM0', 'VVB', 'VVD',
        'VVG', 'VVI', 'VVN', 'VVZ', 'XX0', 'ZZ0', 'AJ0-AV0', 'AJ0-VVN', 'AJ0-VVD',
        'AJ0-NN1', 'AJ0-VVG', 'AVP-PRP', 'AVQ-CJS', 'CJS-PRP', 'CJT-DT0', 'CRD-PNI', 'NN1-NP0', 'NN1-VVB',
        'NN1-VVG', 'NN2-VVZ', 'VVD-VVN', 'AV0-AJ0', 'VVN-AJ0', 'VVD-AJ0', 'NN1-AJ0', 'VVG-AJ0', 'PRP-AVP',
        'CJS-AVQ', 'PRP-CJS', 'DT0-CJT', 'PNI-CRD', 'NP0-NN1', 'VVB-NN1', 'VVG-NN1', 'VVZ-NN2', 'VVN-VVD']

tagIdxs = {}
for i, tag in enumerate(TAGS):
    tagIdxs[tag] = i

for tag in TAGS:
    initProbs[tag] = 0

# divide the training set into sentences
f = open("atestsmall.txt")
lines = f.readlines()
#lines2 = [l.rstrip() for l in lines]

f = open("testingsmall.txt")
print([x.rstrip() for x in f.readlines()])
s = []
all_sentences = []
for i, l in enumerate(lines):
    l = l.rstrip()
    # base case: the word is a colon
    if l[0] == ':':
        l = l.rstrip()
        word = l[0] #the colon word
        l = l[1:] # without the colon
        l = l.split(":")
        l[0] = word
        l = [x.strip() for x in l]
    else:
        l = l.split(':')
        l = [x.strip() for x in l]
    lines[i] = l
    s.append(l)
    if l[0] in ['.', '?', '!', '...']:
        all_sentences.append(s)
        s = []
if s != []:
    all_sentences.append(s) 
#print(lines)
#print(all_sentences[0])

#print(all_sentences[0])
#print(all_sentences[1])
#print(all_sentences[2])
################################################################# initProbs ############################################################################################
# for i in range(len(all_sentences)):
#     initProbs[all_sentences[i][0][1]] += 1
# # normalize (idk if needed?)
# for key in initProbs.keys():
#     initProbs[key] /= len(all_sentences)

### List implementation
initProbs = np.zeros(len(TAGS))
initProbsSize = len(all_sentences)
for i in range(len(all_sentences)):
    initTag = all_sentences[i][0][1] # first tag of each sentence
    idx = tagIdxs[initTag]
    initProbs[idx] += 1
initProbs /= initProbsSize
################################################################ transProbs ############################################################################################
# # initialize: current is key, 2xlen(TAGS) array is value, each index is [tag, probability]
# for keyTag in TAGS:
#     arr = [[x, 0] for x in TAGS]
#     arr.append(['size', 0])
#     transProbs[keyTag] = arr
# #print(transProbs)
# for sentence in all_sentences:
#     for i in range(1, len(sentence)):
#         next = sentence[i][1]
#         current = sentence[i-1][1]
#         index = TAGS.index(next)
#         transProbs[current][index][1] += 1
#         transProbs[current][-1][1] += 1 # increments size = total amout of observations for current
# # normalize the probabilities
# for keyTag in transProbs.keys():
#     curSize = transProbs[keyTag][-1][1]
#     if curSize != 0:
#         for i in range(len(transProbs[keyTag]) - 1): # excludes the size key/value pair
#             transProbs[keyTag][i][1] /= curSize

# # P(S[t+1] | S[t]) = transProbs[S(t)][TAGS.index(S(t+1))][1]

# Matrix implementation
# prior tag is the row, current tag is the column
transProbs = np.zeros((len(TAGS), len(TAGS)))
priorCounts = np.zeros((len(TAGS)))

#print(transProbs)
for sentence in all_sentences:
    for i in range(1, len(sentence)):
        current = sentence[i][1]
        prior = sentence[i-1][1]
        row_idx = tagIdxs[prior]
        col_idx = tagIdxs[current]
        transProbs[row_idx][col_idx] += 1
        priorCounts[row_idx] += 1
for row, count in enumerate(priorCounts):
    if count != 0:
        transProbs[row] /= count

################################################################ obsProbs ################################################################################################
### Matrix implementation
# row: tag
# col: word
# unique words: dict where key = unique word and value = column in the obsProbs matrix
uniqueWordIdxs = {}
idxCounter = 0
obsProbs = np.zeros((len(TAGS),0))
tagCounts = np.zeros(len(TAGS))
# print(obsProbs)
# obsProbs = np.hstack((obsProbs, np.zeros((len(TAGS), 1))))
# obsProbs = np.hstack((obsProbs, np.zeros((len(TAGS), 1))))
# obsProbs = np.hstack((obsProbs, np.zeros((len(TAGS), 1))))
# print(obsProbs[0])
# print(tagCounts)
# print(lines[0])
for l in lines:
    curWord = l[0]
    curTag = l[1]
    tagCounts[tagIdxs[curTag]] += 1
    if curWord not in uniqueWordIdxs:
        # add curWord to uniqueWords
        uniqueWordIdxs[curWord] = idxCounter # idxCounter corresponds to the column curWord represents in obsProbs
        idxCounter += 1
        # add a column to obsProbs
        obsProbs = np.hstack((obsProbs, np.zeros((len(TAGS), 1))))
    row_idx = tagIdxs[curTag]
    col_idx = uniqueWordIdxs[curWord]
    obsProbs[row_idx][col_idx] += 1
# Normalize
for row, count in enumerate(tagCounts):
    if count != 0:
        obsProbs[row] /= count

# print(obsProbs[tagIdxs['NP0']][uniqueWordIdxs['Detective']])
# print(len(uniqueWordIdxs.keys()))
# print(obsProbs[tagIdxs['PUN'],uniqueWordIdxs['.']])
# print(lines)
# print(tagCounts)