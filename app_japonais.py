#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:40 2018

@author: andrei
"""

#project application japense

## Heisig dictionnary look up 
import csv
import sys
import numpy as np
import os
from collections import Counter
import re
from bs4 import BeautifulSoup
import time



class KanjiExample(object):
    def __init__(self, kanjiExample, reading, meaning, exampleJapanese, exampleTranslated):
        
        self.kanjiExample = kanjiExample
        self.reading = reading
        self.meaning = meaning
        self.exampleJapanese = exampleJapanese
        self.exampleTranslated = exampleTranslated

    def __str__(self):
        return self.kanjiExample + ' |' + self.reading  + ' |' + self.meaning  + '\n' + self.exampleJapanese  + '\n' + self.exampleTranslated  + '\n'


class Kanji(object):
    def __init__(self, kanji, keyword, other_keywords, story_1, story_2, stroke_count, heisig_nb, 
                 lesson_nb, onyomi, kunyomi, components, closest):
        
        self.kanji = kanji
        self.keyword = keyword
        self.other_keywords = other_keywords.split(';')
        self.story_1 = story_1
        self.story_2 = story_2
        self.stroke_count = stroke_count
        self.heisig_nb = heisig_nb
        self.lesson_nb = lesson_nb
        self.onyomi = onyomi.split(';')
        self.kunyomi = kunyomi.split(';')
        self.components = components.split(';')
        self.closest = closest.split(';')
        self.examples = list()
        
    def getKanji(self):
        return self.kanji
    def getKeyword(self):
        return self.keyword
    def getOther_keywords(self):
        return self.other_keywords
    def getStory_1(self):
        return self.story_1
    def getStory_2(self):
        return self.story_2
    def getStroke_count(self):
        return self.stroke_count
    def getHeisig_nb(self):
        return self.heisig_nb
    def getLesson_nb(self):
        return self.lesson_nb
    def getOnyomi(self):
        return self.on_yomi   
    def getKunyomi(self):
        return self.kunyomi  
    def getComponents(self):
        return self.components
    def getClosest(self):
        return self.closest
    def incrementExample(self, kanjiExample, reading, meaning, exampleJapanese, exampleTranslated):
        self.examples.append(KanjiExample(kanjiExample, reading, meaning, exampleJapanese, exampleTranslated))
        
    
    def __str__(self):
        return self.kanji + ': ' + self.keyword
    


kanjiDict = dict()
kanji_list = list()
with open('kanjis_heisig.csv', 'rU') as csvfile :
    fi = csv.reader(csvfile, delimiter=str('\t'))
    for i, row in enumerate(fi):
        temp = Kanji(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
                            row[8], row[9], row[10], row[11])
        kanji_list.append(temp)
        kanjiDict[row[0]] = temp


counter = 0
kanjis = list()
with open('Japanese Core Vocab.txt', 'rU') as csvfile :
    fi = csv.reader(csvfile, delimiter=str('\t'))
    for i, row in enumerate(fi):
        for symbol in row[2]:
            try:
               kanjiDict[symbol].incrementExample(row[2], row[4], row[5], row[8], row[9])
               counter += 1
            except:
                pass
                  


def search_kanji(keyword):
    candidate = list()
    candidate_prime = list()
    for k in kanji_list:
        if (keyword == k.getKeyword()) or (keyword in k.getOther_keywords()):
            candidate_prime.append(k)
        elif keyword in k.closest:
                candidate.append(k)
    if len(candidate_prime) == 0:
        if len(candidate) == 0:
            candidate = None
    else:
        candidate = candidate_prime
    return candidate

def search_kanji_simple(keyword):
    for k in kanji_list:
        if keyword == k.getKeyword():
            return k

def kanji_to_keyword(kanji):
    for k in kanji_list:
        if kanji == k.getKanji():
            return k
            break


def overlap_list(list1, list2):
    count = 0
    copy_list1 = list1[:]
    copy_list2 = list2[:]
    for element in list1:
        if element in copy_list2:
            copy_list1.remove(element)
            copy_list2.remove(element)
            count +=1
    return count

def print_kanji_search_by_component(result):
    if type(result) == Kanji:
        print(result.getKanji() + ': ' + result.getKeyword())
    elif type(result) == type(list()) and len(result) >0:
        for k in result:
            print(k.getKanji() + ': ' + k.getKeyword())
    else:
        print('Kanji not found')


def search_kanji_by_primitive(primitives):
    primitives = primitives.split(',')
    candidate = list()
    scores = list()
    for k in kanji_list:
        if (len(primitives) == len(k.getComponents())) and (overlap_list(primitives, k.getComponents()) == len(primitives)):
            candidate.append(k)
            break
        elif overlap_list(primitives, k.getComponents()) > 0:
            min_len =  np.min([len(k.getComponents()), len(primitives)])
            score = np.float(overlap_list(primitives, k.getComponents())) / min_len
            score -= min_len - overlap_list(primitives, k.getComponents())
            scores.append(score)
            candidate.append(k)
    if type(candidate) == type(list()):
        if len(candidate) == 0:
            candidate = None
        else:
            index_scores = [i[0] for i in sorted(enumerate(-np.array(scores)), key=lambda x:x[1])][:np.min([10, len(scores)])]
            candidate = [candidate[i] for i in index_scores]
    
    print(print_kanji_search_by_component(candidate))


def print_special(query_kanji):
    dup_factor_list = list()
    for k in query_kanji:
        if type(k) == type(list()):
            dup_factor_list.append(len(k))
        else:
            dup_factor_list.append(1)
    dup_factor = np.cumprod(np.asarray(dup_factor_list))[-1]

    full_result = list()
    for i, k in enumerate(query_kanji):           
        if type(k) == Kanji:
            temp = [k.kanji] * dup_factor
        elif type(k) == type(list()):
            dup_factor_list_copy = dup_factor_list[:]
            dup_factor_list_copy.pop(i)
            dup_factor_temp = np.cumprod(dup_factor_list_copy)[-1]
            temp = [kk.kanji for kk in k] * dup_factor_temp
        else:
            temp = ['keyword_not_found'] * dup_factor
        full_result.append(temp)
        
    for i in range(dup_factor):
        temp = ''
        for j in range(len(query_kanji)):
            temp += full_result[j][i]
        print(temp)
            
def dictionary(kanji_string):
    keywords = kanji_string.split(',')
    result = list()
    for k in keywords:
        result.append(search_kanji(k))
    if len(result) == 1:
        print(result[0][0])
    else:
        print_special(result)

 


'''
search_kanji_by_primitive('tree,glued to')
temp = dictionary('contraption') 
kanji_string = search_kanji('isolate')
print dictionary('contraption').getKanji() + ' ' +  dictionary('contraption').getKeyword()

for k in kanji_string:
    print k
    
print '\n'
count_lesson = list()
for k in kanji_list:
    try:
        count_lesson.append(int(k.getLesson_nb()))
    except:
        pass

lesson_frequ = Counter(count_lesson)

count_lesson = list()
for i in range(57):
    count_lesson.append(lesson_frequ[i])
lesson_cum = np.cumsum(np.asarray(count_lesson))
'''

temp = search_kanji('mechanism')

def kanji_review(lesson_nb = range(57), number = 200):
    kanji_of_interest = list()
    wrong_kanjis = list()

    for k in kanji_list:
        try:
            if int(k.getLesson_nb()) in lesson_nb:
                kanji_of_interest.append(k)
        except:
            pass
    
    print(str(len(kanji_of_interest)))
    i = 0
    for j in range(number):
        random_index = np.random.randint(len(kanji_of_interest))
        print(kanji_of_interest[random_index].getKanji())
        answer = input()  # Python 2
        i += 1
        if len(kanji_of_interest[random_index].examples) > 3:
            randomIndexExample = np.random.randint(0, len(kanji_of_interest[random_index].examples),3)
            for riE in randomIndexExample:
                print(kanji_of_interest[random_index].examples[riE])
        else:
            for example in kanji_of_interest[random_index].examples:
                print(example)
        if answer != kanji_of_interest[random_index].getKeyword():
            print(answer + ' vs ' + kanji_of_interest[random_index].getKeyword())
            print('ok nonetheless?')
            answer_revision = input()
            if answer_revision != 'ok':
                temp = search_kanji_simple(answer)
                try:
                    print('you confused ' + temp.getKanji() + ' (' + temp.getKeyword() + ') with ' + kanji_of_interest[random_index].getKanji() + ' (' + kanji_of_interest[random_index].getKeyword() + ')')
                    print('\n')
                except:
                    pass
                print ('Answer: ' +  kanji_of_interest[random_index].getKeyword())
                print (kanji_of_interest[random_index].getComponents())
                print ('\n')
                print (kanji_of_interest[random_index].getStory_1())
                print ('\n')
                print (kanji_of_interest[random_index].getStory_2())
                print ('\n')
                print ('\n')
                wrong_kanjis.append(kanji_of_interest[random_index].getKanji() + ';' + answer)
                i-=1
                time.sleep(15)
        kanji_of_interest.pop(random_index)
        
        print(str(i) + ' / ' + str(number - j - 1))
    return wrong_kanjis




def main():
    # print command line arguments
    if sys.argv[1] == "test":
        wrong_kanjis = kanji_review(number = 33)
        list_to_save = ','.join(wrong_kanjis)
        
        f = open("forgotten_kanji.txt", "a");
        f.write(list_to_save)
        f.close()
    elif sys.argv[1] == "vocabulary":
        while(True):
            kanji_to_look = input()
            try:
                result = search_kanji(kanji_to_look)
                for r in result:
                    print(r.getKanji() + ': ' + r.getKeyword())
            except:
                result = kanji_to_keyword(kanji_to_look)
                print(result.getKanji() + ': ' + result.getKeyword())

                


            
if __name__ == "__main__":
    main()


'''
lesson_frequ = Counter(lessons)
count_lesson = list()
for i in range(57):
    count_lesson.append(lesson_frequ[i])

lesson_cum = np.cumsum(np.asarray(count_lesson))


def trim_components(comp):
    comp = re.sub(',',';', comp)
    temp = comp.split('<br>')
    temp2 = [t.split(';') for t in temp]
    temp_final = temp2[:]
    for i in range(len(temp2)):
        for j in range(len(temp2[i])):
            temp_final[i][j] = re.sub('radical.*','', (re.sub('.*: ', '',temp2[i][j]))).lstrip().rstrip()
    for i in range(len(temp2)):
        temp_final[i] = list(set(temp_final[i]))
    return temp_final
    
'''   