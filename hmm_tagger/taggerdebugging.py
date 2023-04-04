import os
import sys
import argparse
import numpy as np

def makeInitialProbabilities(TAGS, tagIdxs, all_sentences):
    initProbs = np.zeros(len(TAGS))
    initProbsSize = len(all_sentences)
    for i in range(len(all_sentences)):
        initTag = all_sentences[i][0][1] # first tag of each sentence
        idx = tagIdxs[initTag]
        initProbs[idx] += 1
    initProbs /= initProbsSize

    return initProbs

def makeTransitionProbabilities(TAGS, tagIdxs, all_sentences):
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
    
    return transProbs

def makeObservationProbabilities(TAGS, tagIdxs, lines):
    ### Matrix implementation
    # row: tag
    # col: word
    # unique words: dict where key = unique word and value = column in the obsProbs matrix
    uniqueWordIdxs = {}
    idxCounter = 0
    obsProbs = np.zeros((len(TAGS),0))
    tagCounts = np.zeros(len(TAGS))

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

    return obsProbs, uniqueWordIdxs

def viterbi(E, S, I, T, M, uniqueWordIdxs):
    # E: set of observations (words in a sentence of the test file)
    # S: set of all states (TAGS array)
    # I: Initial Probability Matrix
    # T: Transitional Probability Matrix: P(s[t+1] | s[t])
    # M: observation Probability Matrix: P(E[t] | S[t])
    prob = np.zeros((len(E), len(S)))
    prev = np.zeros((len(E), len(S)))

    # Determine values for time step 0
    for i in range(len(S)):
        prob[0, i] = I[i] * M[i, uniqueWordIdxs[E[0]]]
        prev[0, i] = None
    
    # for time steps 1 to length(E)-1, find each current state's most likely prior state
    for t in range(1, len(E)):
        for i in range(len(S)):
            x = np.argmax(prob[t-1,:]* T[:,i]* M[i, uniqueWordIdxs[E[t]]])
            prob[t, i] = prob[t-1, x] * T[x, i] * M[i, uniqueWordIdxs[E[t]]]
            prev[t,i] = x
    return prob, prev

def makeObservationSet(testfile):
    s = []
    testSentences = []
    f = open(testfile)
    lines = [x.rstrip() for x in f.readlines()]
    for l in lines:
        s.append(l)
        if l in ['.', '?', '!', '...']:
            testSentences.append(s)
            s = []
    if s != []:
        testSentences.append(s)
    return testSentences
        

def getSolutionTags(prob, prev, TAGS, observations):
    '''Returns a string solution for one sentence '''
    solString = ''
    solutions = [] # equal to length of recorded observations
    startIdx = np.argmax(prob[-1])
    # solutions.insert(0, TAGS[startIdx])
    backtrack = [startIdx]
    for i in range(len(prob)-1, 0, -1):
        idx = backtrack[0]
        solutions.insert(0, TAGS[idx])
        prevTagIdx = prev[i][idx]
        backtrack.insert(0, int(prevTagIdx))
        # string the result
        temp = f'{observations[i]} : {TAGS[idx]}\n'
        solString = temp + solString        
    # above loop gets tags for observations 1 to len(evidence) - 1: run once more to get the first tag (for evidence 0)
    idx = backtrack[0]
    solutions.insert(0, TAGS[idx])
    temp = f'{observations[0]} : {TAGS[idx]}\n'
    solString = temp + solString

    return solString

def writeSolution(solString, outputFile):
    output = open(outputFile, 'w')
    output.write(solString)
    output.close()
    return

if __name__ == '__main__':

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--trainingfiles",
    #     action="append",
    #     nargs="+",
    #     required=True,
    #     help="The training files."
    # )
    # parser.add_argument(
    #     "--testfile",
    #     type=str,
    #     required=True,
    #     help="One test file."
    # )
    # parser.add_argument(
    #     "--outputfile",
    #     type=str,
    #     required=True,
    #     help="The output file."
    # )
    # args = parser.parse_args()

    # training_list = args.trainingfiles[0]
    # print("training files are {}".format(training_list))

    # print("test file is {}".format(args.testfile))

    # print("output file is {}".format(args.outputfile))


    # print("Starting the tagging process.")

    ###################################################### Tags Initializer #################################################################################################
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
    
    ################################################### Sentence/Lines Initializer ##########################################################################################

    # divide the training set into sentences
    # for trainingList in args.inputfiles:
    f = open("mytraining.txt") # OPEN THE TRAINING FILE: NEEED TO FIX THIS
    lines = f.readlines()

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

    initProbs = makeInitialProbabilities(TAGS, tagIdxs, all_sentences)
    transProbs = makeTransitionProbabilities(TAGS, tagIdxs, all_sentences)
    obsProbs, uniqueWordIdxs = makeObservationProbabilities(TAGS, tagIdxs, lines)

    ############################################################ Test Construction #########################################################################################

    testSentences = makeObservationSet('mytesting.txt') #args.testfile

    ############################################################## Algorithm Run #########################################################################################
    solution = ''
    for test_sentence in testSentences:
        prob, prev = viterbi(test_sentence, TAGS, initProbs, transProbs, obsProbs, uniqueWordIdxs)
        print(np.argmax(prob[-1]))
        solString = getSolutionTags(prob, prev, TAGS, test_sentence)
        solution += solString
    
    writeSolution(solution, 'myoutput.txt') # args.outputfile

    