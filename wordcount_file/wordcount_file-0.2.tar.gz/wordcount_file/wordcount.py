
def count_words(word_list, word_dict={}, case_sensitive=False):
    """
    Count the words in a list and merge with word_dict if included
    return word_dict
    """
    for word in word_list:
        # change case and remove any punctuations at the start/end of word #
        if word:
            # if not case sensitive change words to lower case
            if not case_sensitive:
                w = word.lower()
            # strip any leading dos carriage returns and line feeds
            while w.endswith('\n') or w.endswith('\r'):
                w = w.rstrip('\n')
                w = w.rstrip('\r')
            # move to next word in list if nothing to process
            if not w:
                continue

            # check single char items
            if len(w) == 1:
                if not w.isalnum():
                    # skip any non alphanumeric single chars
                    continue
            else:
                # strip any non alphanumeric first and last chars
                if not w[0].isalnum():
                    w = w[1:]
                if not w[-1].isalnum():
                    w = w[:-1]

            # Increment word count or add to dictionary
            if w in word_dict.keys():
                word_dict[w] += 1
            else:
                word_dict[w] = 1

    return word_dict


class WordCount:
    """
    Count the words in an ascii text file
    Words separated by SEPARATORS are counted
        SEPARATORS = [' ',';',':','=',',','(',')','{','}','[',']','|','<','>']

    self.words      = Dictionary of words and each count
    self.counts     = Dictionary of counts with a list of each words
    self.textfile   = File processed
    self.all_words  = Total number of counted words
    self.word_count = Total number of all words in file
    """

    def __init__(self, textfile, case_sensitive=False):
        """
        initialize with textfile
        """
        from collections import OrderedDict

        self.words = {}
        self.counts = {}
        self.textfile = textfile
        self.word_count = 0
        SEPARATORS = [' ',';',':','=',',','(',')','{','}','[',']','|','<','>']
        with open(textfile, 'r') as f:
            for line in f:
                _words_in_line = [line]
                # split words by separators #
                for sep in SEPARATORS:
                    line, _words_in_line = _words_in_line, []
                    for seq in line:
                        _words_in_line += seq.split(sep)
                #_words_in_line = line.split(' ')

                if _words_in_line:
                    self.word_count += len(_words_in_line)
                    self.words = count_words(_words_in_line, self.words, case_sensitive)

        # create counts dictionary for faster count sorting #
        for _word in self.words:
            count = self.words[_word]
            if count in self.counts:
                self.counts[count].append(_word)
            else:
                self.counts[count] = [ _word ]
        self.counts = OrderedDict(sorted(self.counts.items(), reverse=True))

        self.all_words = len(self.words.keys())

    def __repr__(self):
        return "{ 'textfile': '%s', 'word_count': %s }" % (self.textfile, self.word_count)

    def show_topwords(self, num=5):
        """
        print the topwords (default = top 5 words)
        """
        count = 0
        for _count in self.counts:
            if count < num:
                print "%i => %s" % (_count, self.counts[_count])
                count += 1
            else:
                return


