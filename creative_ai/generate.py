#!/usr/bin/env python
import sys
sys.dont_write_bytecode = True # Suppress .pyc files

import random
import spacy

from creative_ai.pysynth import pysynth
from creative_ai.utils.menu import Menu
from creative_ai.data.dataLoader import *
from creative_ai.models.musicInfo import *
from creative_ai.models.languageModel import LanguageModel

# FIXME Add your team name
TEAM = 'SICKO CODE'
LYRICSDIRS = ['xmas']
TESTLYRICSDIRS = ['the_beatles_test']
MUSICDIRS = ['gamecube']
WAVDIR = 'wav/'

def output_models(val, output_fn = None):
    """
    Requires: nothing
    Modifies: nothing
    Effects:  outputs the dictionary val to the given filename. Used
              in Test mode.

    This function has been done for you.
    """
    from pprint import pprint
    if output_fn == None:
        print("No Filename Given")
        return
    with open('TEST_OUTPUT/' + output_fn, 'wt') as out:
        pprint(val, stream=out)

def sentenceTooLong(desiredLength, currentLength):
    """
    Requires: nothing
    Modifies: nothing
    Effects:  returns a bool indicating whether or not this sentence should
              be ended based on its length.

    This function has been done for you.
    """
    STDEV = 1
    val = random.gauss(currentLength, STDEV)
    return val > desiredLength

def printSongLyrics(verseOne, verseTwo, chorus):
    """
    Requires: verseOne, verseTwo, and chorus are lists of lists of strings
    Modifies: nothing
    Effects:  prints the song.

    This function is done for you.
    """
    verses = [verseOne, chorus, verseTwo, chorus]

    print()
    for verse in verses:
        for line in verse:
            print((' '.join(line)).capitalize())
        print()

def trainLyricModels(lyricDirs, lyricsOrGrammar, test=False):
    """
    Requires: lyricDirs is a list of directories in data/lyrics/
    Modifies: nothing
    Effects:  loads data from the folders in the lyricDirs list,
              using the pre-written DataLoader class, then creates an
              instance of each of the NGramModel child classes and trains
              them using the text loaded from the data loader. The list
              should be in tri-, then bi-, then unigramModel order.
              Returns the list of trained models.

    This function is done for you.
    """
    model = LanguageModel()
    grammarModel = LanguageModel()

    for ldir in lyricDirs:
        lyrics = prepData(loadLyrics(ldir))
        model.updateTrainedData(lyrics)

        grammarBool = False
        grammarModel.updateTrainedData(lyrics, grammarBool)
        print(model)

    if not lyricsOrGrammar:
        return model
    else:
        return grammarModel

def trainMusicModels(musicDirs):
    """
    Requires: musicDirs is a list of directories in data/midi/
    Modifies: nothing
    Effects:  works exactly as trainLyricsModels, except that
              now the dataLoader calls the DataLoader's loadMusic() function
              and takes a music directory name instead of an artist name.
              Returns a list of trained models in order of tri-, then bi-, then
              unigramModel objects.

    This function is done for you.
    """
    model = LanguageModel()

    for mdir in musicDirs:
        music = prepData(loadMusic(mdir))
        model.updateTrainedData(music)

    return model

def runLyricsGenerator(models, gModels):
    """
    Requires: models is a list of a trained nGramModel child class objects
    Modifies: nothing
    Effects:  generates a verse one, a verse two, and a chorus, then
              calls printSongLyrics to print the song out.
    """
    verseOne = []
    verseTwo = []
    chorus = []

    for x in range(4):
        sentence = generateTokenSentence(models, gModels, 7)
        verseOne.append(sentence)
        if x == 1:
            rhyme = findRhyme(models, sentence[-1])
        if x == 3:
            sentence[-1] = rhyme

    for x in range(4):
        sentence = generateTokenSentence(models, gModels, 7)
        verseTwo.append(sentence)
        if x == 1:
            rhyme = findRhyme(models, sentence[-1])
        if x == 3:
            sentence[-1] = rhyme

    for x in range(3):
        sentence = generateTokenSentence(models, gModels, 7)
        chorus.append(sentence)
        if x == 1:
            repeat = sentence
        if x == 0:
            rhyme = findRhyme(models, sentence[-1])
        if x == 2:
            sentence[-1] = rhyme
    chorus.append(repeat)

    printSongLyrics(verseOne, verseTwo, chorus)

def runMusicGenerator(models, songName):
    """
    Requires: models is a list of trained models
    Modifies: nothing
    Effects:  uses models to generate a song and write it to the file
              named songName.wav
    """

    verseOne = []
    verseTwo = []
    chorus = []

    for i in range(4):
        verseOne.extend(generateTokenSentence(models, 7))
        verseTwo.extend(generateTokenSentence(models, 7))
        chorus.extend(generateTokenSentence(models, 9))

    song = []
    song.extend(verseOne)
    song.extend(verseTwo)
    song.extend(chorus)
    song.extend(verseOne)
    song.extend(chorus)

    pysynth.make_wav(song, fn=songName)

###############################################################################
# Begin Core >> FOR CORE IMPLEMENTION, DO NOT EDIT OUTSIDE OF THIS SECTION <<
###############################################################################

def generateTokenSentence(model, gModel, desiredLength):
    """
    Requires: model is a single trained languageModel object.
              desiredLength is the desired length of the sentence.
    Modifies: nothing
    Effects:  returns a list of strings where each string is a word in the
              generated sentence. The returned list should NOT include
              any of the special starting or ending symbols.

              For more details about generating a sentence using the
              NGramModels, see the spec.
    """
    sentence = []
    nextWord = model.getNextToken(sentence)
    nextGrammar = gModel.getNextToken(sentence)
    count = 0
    desiredSyllableCount = 7

    nlp = spacy.load('en_core_web_sm')

    while (count < desiredSyllableCount):
            #while((not sentenceTooLong(desiredLength, len(sentence))) and (nextWord != "$:::$")):
        if nextWord == "$:::$":
            nextWord = model.getNextToken(sentence)
        elif nextWord == "^::^" or nextWord == "^:::^":
            nextWord = model.getNextToken(sentence)
        else:
            sentence.append(nextWord)
            count += syllables(nextWord)
            nextWord = model.getNextToken(sentence)
            '''
            doc = nlp(nextWord)
            if doc.pos_ == nextGrammar:
                sentence.append(nextWord)
                count += syllables(nextWord)
                nextWord = model.getNextToken(sentence)
                nextGrammar = gModel.getNextToken(sentence)
            '''
    return sentence

def listToString(list):
    sentence = ""
    for i in range(len(list)):
        sentence += list[i]
    return sentence

def syllables(word):
    count = 0
    vowels = 'aeiouy'
    word = word.lower()
    if word[0] in vowels:
        count +=1
    for index in range(1,len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count +=1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count+=1
    if count == 0:
        count +=1
    return count

def checkRhyme(wordOne, wordTwo):
    if len(wordOne) > 2 or len(wordTwo) > 2:
        isMatching = False
        temp = wordOne[-3:]
        temp2 = wordTwo[-3:]
        if temp == temp2:
            isMatching = True
        return isMatching
    elif len(wordOne) > 1 or len(wordTwo) > 1:
        isMatching = False
        temp = wordOne[-2:]
        temp2 = wordTwo[-2:]
        if temp == temp2:
            isMatching = True
        return isMatching
    return True

def findRhyme(model, word):
    sentence = []
    nextWord = model.getNextToken(sentence)
    rhymeCheck = checkRhyme(word, nextWord)
    while rhymeCheck == False:
        nextWord = model.getNextToken(sentence)
        rhymeCheck = checkRhyme(word, nextWord)
    return nextWord


###############################################################################
# End Core
###############################################################################

###############################################################################
# Main
###############################################################################

PROMPT = [
    'Generate song lyrics by Migos',
    'Generate a song using data from Nintendo Gamecube',
    'Quit the music generator'
]

def main():
    """
    Requires: Nothing
    Modifies: Nothing
    Effects:  This is your main function, which is done for you. It runs the
              entire generator program for both the reach and the core.

              It prompts the user to choose to generate either lyrics or music.
    """

    mainMenu = Menu(PROMPT)

    lyricsTrained = False
    musicTrained = False

    print('Welcome to the {} music generator!'.format(TEAM))
    while True:
        userInput = mainMenu.getChoice()

        if userInput == 1:
            if not lyricsTrained:
                print('Starting lyrics generator...')
                lyricsOrGrammar = False
                lyricsModel = trainLyricModels(LYRICSDIRS, lyricsOrGrammar)
                lyricsTrained = True
                lyricsOrGrammar = True
                grammarModel = trainLyricModels(LYRICSDIRS, lyricsOrGrammar)

            runLyricsGenerator(lyricsModel, grammarModel)

        elif userInput == 2:
            if not musicTrained:
                print('Starting music generator...')
                musicModel = trainMusicModels(MUSICDIRS)
                musicTrained = True

            songName = input('What would you like to name your song? ')

            runMusicGenerator(musicModel, WAVDIR + songName + '.wav')

        elif userInput == 3:
            print('Thank you for using the {} music generator!'.format(TEAM))
            sys.exit()

# This is how python tells if the file is being run as main
if __name__ == '__main__':
    main()
    # note that if you want to individually test functions from this file,
    # you can comment out main() and call those functions here. Just make
    # sure to call main() in your final submission of the project!
