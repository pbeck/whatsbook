#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
wa2latex.py

(c) Pelle Beckman, 2016
Licensed under the MIT License.

Reformats data from WhatsApp chat logs for LaTeX.
See https://github.com/pbeck/whatsbook for more info.

Uses code from socialmediaparse
(github.com/seandolinar/socialmediaparse).

Requires python3 and pandas
'''

import io
import sys
import re
import os
import pandas as pd

class EmojiHandler(object):

    def __init__(self):

        #loads the emoji table in the data folder in the package
        file_path = os.path.dirname(os.path.abspath(__file__))
        emoji_key = pd.read_csv(file_path + '/data/' + 'emoji_table.txt', encoding='utf-8', index_col=0)

        #loads the diversity table
        diversity_df = pd.read_csv(file_path + '/data/' + 'diversity_table.txt', encoding='utf-8', index_col=0)
        
        #intialize emoji count
        emoji_key['count'] = 0
        emoji_dict = emoji_key['count'].to_dict()
        emoji_dict_total = emoji_key['count'].to_dict()

        #initialize diversity analysis
        diversity_df['count'] = 0
        diversity_keys = diversity_df['count'].to_dict().keys()
        human_emoji = []

        for emoji in diversity_keys:

            emoji = emoji.replace(u'\U0001f3fb', '')
            emoji = emoji.replace(u'\U0001f3fc', '')
            emoji = emoji.replace(u'\U0001f3fd', '')
            emoji = emoji.replace(u'\U0001f3fe', '')
            emoji = emoji.replace(u'\U0001f3ff', '')

            human_emoji.append(emoji)

        human_emoji_unique = list(set(human_emoji))
        human_emoji_dict = {}

        for emoji in human_emoji_unique:

            human_emoji_dict[emoji] = 0

        self.dict = emoji_dict
        self.dict_total = emoji_dict_total
        self.emoji_list = emoji_dict.keys()
        self.baskets = []
        self.total_emoji = 0
        self.total_indiv_emoji = 0

        self.skin_tones = ['\U0001f3fb', '\U0001f3fc', '\U0001f3fd', '\U0001f3fe', '\U0001f3ff']
        self.skin_tones_dict = {'human_emoji': 0, '\U0001f3fb':0, '\U0001f3fc':0, '\U0001f3fd': 0, '\U0001f3fe':0, '\U0001f3ff':0}
        self.human_emoji = human_emoji_unique
        self.human_emoji_dict = human_emoji_dict


    def replace_emoji(self, text):

        for emoji in self.emoji_list:

            if emoji in text:
                text = text.replace(emoji, "\\emoji{" + str(emoji) + "}")
                text = text.replace("\"", "")
                text = text.replace(u"\\U000", "")
                text = text.replace(u"\\u000", "")

        for emoji in self.human_emoji:
            if emoji in text:
                text = text.replace(emoji, "\\emoji{" + str(emoji) + "}")
                #text = text.replace(u"\\U000", "")
        return text


if __name__ == '__main__':

    # No input given, print usage and exit
    if len(sys.argv) == 1:        
        print("No file argument given. Exiting.")
        exit(1)


    emojis = EmojiHandler()

    prevdate = None

    with io.open(sys.argv[1], 'r', encoding="utf-8") as f:
        for line in f.readlines():
        
            # Remove trailing newline chars
            line = line.rstrip()

            # Skip if empty line
            if line in ['', '\n', '\r\n']:
                continue
            
            # Replace media attachments with \includegraphics{}
            # Note: the [H] in \begin{figure}[H] forces insertion of
            # figure at text position.
            # http://tex.stackexchange.com/questions/32886/
            # how-to-fit-a-large-figure-to-page
            # TODO: Handle video? (.mp4, .mov, etc)
            media_att = re.search("([a-zA-Z0-9-_]+).jpg", line)
            if media_att:
                line = re.sub("([a-zA-Z0-9-_]+).jpg", r'\n\\begin{figure}[H]\n' +
                    r'\\includegraphics[cfbox=lightgray 0.5pt 0pt, width=\\textwidth,keepaspectratio]{' + media_att.group(0) + r'}\n' +
                    r'\\end{figure}\n', line)

            # Remove timestamps
            line = re.sub("\d{2}:\d{2}:\d{2}:\s", "", line)

            # Replace LaTeX reserved chars
            # TODO: This also replaces chars is URLs - it shouldn't
            # TODO: Should also include #, $, %, ^, _, {, }, ~, \
            # TODO: Make better.
            line = line.replace("&", "\\&")
            line = line.replace("$", "\\$")
            line = line.replace("#", "\\#")
            line = line.replace("%", "\\%")

            # Fix links to LaTeX command '\url{}'
            # http://stackoverflow.com/questions/6883049/
            # regex-to-find-urls-in-string-in-python
            url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", line)
            if url:
                line = re.sub(url.re.pattern, "\\url{" + url.group(0) + "}", line)

            # Remove various cruft (might require editing for localized stuff)
            line = re.sub("<.*>", "", line)

            line = emojis.replace_emoji(line)

            # Add LaTeX line ending command: '\\*'
            line = line + "\\\\*"

            #######################
            # Insert custom names
            #######################
            line = line.replace("Username 1: ", "\\chas ")
            line = line.replace("Username 2: ", "\\margot ")
            line = line.replace("Username 3", "\\dudley ")
            
            # Keep only first occurence of dates and
            # format them as sections; '\section*{<date>}'
            # (the * removes numbering - TeX command)
            # TODO: Some lines do not start with dates
            date = line.split(" ")[0]
            if prevdate != date:
                if sys.platform == 'win32':
                    print(u"\section*{%s}" % date.encode('unicode-escape'))
                else:
                    print(u"\section*{%s}" % date)

            output_line = u" ".join(line.split(" ")[1:])
            #output_line = " ".join(str(item) for item in line.split(" "))
            #output_line = u" ".join(line.split(" ")[1:])
            print(output_line.encode('utf-8'))
            prevdate = date
