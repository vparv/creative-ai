#!/usr/bin/env python
import sys
sys.dont_write_bytecode = True # Suppress .pyc files

import random
import spacy
import tweepy

from creative_ai.pysynth import pysynth
from creative_ai.utils.menu import Menu
from creative_ai.data.dataLoader import *
from creative_ai.models.musicInfo import *
from creative_ai.models.languageModel import LanguageModel

# FIXME Add your team name
TEAM = 'SICKO CODE'
LYRICSDIRS = ['xmas']
TESTLYRICSDIRS = ['the_beatles']
MUSICDIRS = ['gamecube']
WAVDIR = 'wav/'

global twitterString
twitterString = ""

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

def trainLyricModels(lyricDirs, test=False):
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

    for ldir in lyricDirs:
        lyrics = prepData(loadLyrics(ldir))
        model.updateTrainedData(lyrics)

    return model

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

def runLyricsGenerator(models, name):
    """
    Requires: models is a list of a trained nGramModel child class objects
    Modifies: nothing
    Effects:  generates a verse one, a verse two, and a chorus, then
              calls printSongLyrics to print the song out.
    """
    verseOne = []
    verseTwo = []
    chorus = []

    verseOneCount = 0
    firstLine = ["Merry", "Christmas", name]
    verseOne.append(firstLine)
    while verseOneCount < 4:
        sentence = generateTokenSentence(models, 7)
        if spacyCheck(listToString(sentence)):
            verseOne.append(sentence)
            if verseOneCount == 1:
                rhyme = findRhyme(models, sentence[-1])
            if verseOneCount == 3:
                sentence[-1] = rhyme
            verseOneCount += 1

    verseTwoCount = 0
    while verseTwoCount < 4:
        sentence = generateTokenSentence(models, 7)
        if spacyCheck(listToString(sentence)):
            verseTwo.append(sentence)
            if verseTwoCount == 1:
                rhyme = findRhyme(models, sentence[-1])
            if verseTwoCount == 3:
                sentence[-1] = rhyme
            verseTwoCount += 1

    twitterString = ""
    chorusCount = 0
    while chorusCount < 3:
        sentence = generateTokenSentence(models, 7)
        if spacyCheck(listToString(sentence)):
            chorus.append(sentence)
            if chorusCount == 1:
                repeat = sentence
            if chorusCount == 0:
                rhyme = findRhyme(models, sentence[-1])
            if chorusCount == 2:
                sentence[-1] = rhyme
            chorusCount += 1
    chorus.append(repeat)

    printSongLyrics(verseOne, verseTwo, chorus)

    for list in verseOne:
        twitterString += listToString(list) + "\n"
    twitterString += "\n"
    for list in chorus:
        twitterString += listToString(list) + "\n"

    charCount = 0
    for word in twitterString:
        charCount += len(word)
    if charCount > 280:
        twitterString = "Please try again: name too long"

    print (twitterString)
    return twitterString

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

def generateTokenSentence(model, desiredLength):
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
    count = 0
    desiredSyllableCount = 7
    currentWordSyllable = 0

    while (count < desiredSyllableCount):
        count += currentWordSyllable
        if nextWord == "$:::$":
            sentence.append("")
            nextWord = model.getNextToken(sentence)
        elif nextWord == "^::^" or nextWord == "^:::^":
            nextWord = model.getNextToken(sentence)
        else:
            sentence.append(nextWord)
            currentWordSyllable = syllables(nextWord)
            nextWord = model.getNextToken(sentence)

    return sentence


def spacyCheck(sentence):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(sentence)

    if doc[-1].pos_ == "DET" or doc[-1].pos_ == "ADP" or doc[-1].pos_ == "AUX" or doc[-1].pos_ == "INTJ" or doc[-1].pos_ == "CONJ" or doc[-1].pos_ == "CCONJ" or doc[-1].pos_ == "SCONJ" or doc[-1].pos_ == "PART":
        return False
    return True

def listToString(list):
    sentence = ""
    for i in range(len(list)):
        sentence += list[i] + " "
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
    'Generate xmas song lyrics',
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
                lyricsModel = trainLyricModels(LYRICSDIRS)
                lyricsTrained = True

            name = input("For whom is this Christmas song addressed? ")
            name += "!"
            twitterString = runLyricsGenerator(lyricsModel, name)


            consumer_key = 'QyX2wwasqJsQKRKXYiiKxZqBD'
            consumer_secret = 'rKlMSyPpsXT6tAl6VQxzlyq6lIbpl8QTgy7lu7uXFw4xljNXUR'
            access_token = '837827575124721664-4NCF1WTrdHPUKAS4Th4pb0vwIWLv5n9'
            access_token_secret = 'wTwle1sldbgcjqevgD8rwYCWNEkLDi6QVxd3qYS9qSAse'

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)

            user = api.me()
            print(user.name)
            print(user.location)
            #print(twitterString)
            api.update_status(twitterString)
            print("Sicko Code 183 wishes you a Merry Christmas")

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
