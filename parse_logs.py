#! /usr/bin/env python3
import re
import math
import argparse


def remove_timestamp(string):
    return string[9:]


def parse_phrase(phrase, person='Клиент'):
    if person == 'Клиент':
        phrase = re.split("[\:\-\.!?\s]+", phrase)
    else:
        phrase = re.split("\s+", phrase)
    return [x for x in phrase if x]


def count_word_freqs(sentences):
    all_words = 0
    words = {}
    for sentence in sentences:
        for word in sentence:
            all_words += 1
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
    for elem in words.keys():
        words[elem] = math.log(words[elem]/all_words)
    return words


def parse_file(filename):
    chats = []
    sentences = []
    f = open(filename, "r+")
    while True:
        if not f.readline():
            break
        f.readline()
        f.readline()
        s = f.readline().strip()
        chat = []
        person = ""
        current_phrase = ""
        while ('--------' not in s):
            s = remove_timestamp(s)
            person = s[:6]
            if person == 'Клиент':
                current_phrase = s[8:]
            else:
                current_phrase = s[11:]
            current_phrase = parse_phrase(current_phrase)
            sentences.append(current_phrase)
            chat.append((person, current_phrase))
            s = f.readline().strip()
        f.readline()
        chats.append(chat)
    return chats, sentences


def best_dialogs(filename, max_dialog_len=12):
    chats, sentences = parse_file(filename)
    words = count_word_freqs(sentences)
    dialogs = []
    stop_words = ['привет', 'ку', 'кукусики', 'чмоки', 'приветики', 'здарова', 'приветствую',
                  'здравствуйте', 'приффки', 'хай', 'хей', 'добрый', 'доброе', 'доброго', 'спасибо',
                  'ладно', 'ок', 'доброго', 'свидания', 'встреч', 'спокойной', 'наилучшего', 'спс']
    stop_words = set(stop_words)
    for i in range(len(chats)):
        current_chat = chats[i]
        if len(current_chat) > max_dialog_len:
            continue
        min_client_score = 0
        best_question = ""
        best_answer = ""
        min_employee_score = 0
        best_index = 0
        index = 0
        for k in range(len(current_chat)):
            person, sentence = current_chat[k]
            sentence_score = 0
            for word in sentence:
                sentence_score += words[word]
            if person != "Клиент" and k == len(current_chat) - 1:
                sentence_score /= 2
            if person != "Клиент" and sentence_score < min_employee_score:
                best_answer = sentence
                min_employee_score = sentence_score
                best_index = index
            index += 1
        near_sentences = []
        for ind in range(best_index - 4, best_index + 4):
            if ind in range(len(current_chat)):
                person, sentence = current_chat[ind]
                if person != "Клиент":
                    # print(sentence)
                    # if isinstance(sentence, list):
                    #    sentence = " ".join(sentence)
                    # print(sentence)
                    near_sentences.extend(sentence)
        # print(near_sentences[:3])
        # print(type(near_sentences))
        new_near_sentences = []
        for word in near_sentences:
            if word.lower() not in stop_words:
                new_near_sentences.append(word)
        best_answer = new_near_sentences

        for j in range(best_index):
            person, sentence = current_chat[j]
            sentence_score = 0
            for word in sentence:
                sentence_score += words[word]
            if person == "Клиент" and sentence_score < min_client_score:
                best_question = sentence
                min_client_score = sentence_score
        dialogs.append((best_question, best_answer))
    return dialogs


def print_dialogs(dialogs, output_file):
    with open(output_file, 'w') as faq:
        for question, answer in dialogs:
            faq.write(" ".join(question) + '\n')
            faq.write('++++\n')
            faq.write(" ".join(answer) + '\n\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    args = parser.parse_args()
    in_file = args.input
    out_file = args.output
    dialogs = best_dialogs(in_file)
    print_dialogs(dialogs, out_file)

main()
