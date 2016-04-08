import music21
import copy
import musicXML_parsing
import os


class SimpleAlignment:
    attr = ''  # parson || rhythm
    gapped_parse = None
    comparison_parse = None
    gapped_piece = []
    comparison_piece = []
    longest_length = 0
    gapped_bar_num = 0
    min_edit_alignments = []
    min_edit_obj = None
    max_score_alignments = []
    max_score_obj = None
    right_shift = 0
    left_shift = 0

    def __init__(self, gapped, comparison, feat, gap_num):
        self.attr = feat
        self.gapped_parse = gapped
        self.comparison_parse = comparison
        self.gapped_parse.create_gap(gap_num)
        self.gapped_bar_num = gap_num

        if self.attr == 'parson':
            self.gapped_piece = copy.deepcopy(self.gapped_parse).parsons_code
            self.comparison_piece = copy.deepcopy(self.comparison_parse).parsons_code
        elif self.attr == 'rhythm':
            self.gapped_piece = copy.deepcopy(self.gapped_parse).rhythm_hash
            self.comparison_piece = copy.deepcopy(self.comparison_parse).rhythm_hash

        # print self.gapped_piece
        # print self.comparison_piece

        self.base_align()
        self.get_min_edit_obj()

    def get_min_edit_obj(self):
        align_obj = self.max_score_alignments[0]
        align_score = align_obj.alignment_score

        for i in self.max_score_alignments:
            if i.alignment_score > align_score and align_obj.replaced_bar != '':
                align_score = i.alignment_score
                align_obj = i
            elif align_obj.replaced_bar == '':
                align_score = i.alignment_score
                align_obj = i
        self.max_score_obj = align_obj

    def base_align(self):
        gapped_length = len(self.gapped_piece)
        compare_length = len(self.comparison_piece)
        if gapped_length == compare_length:
            self.max_score_alignments.append(Score(self.gapped_piece, self.comparison_piece, self.gapped_bar_num - 1))
        elif gapped_length > compare_length:
            extended_piece = copy.deepcopy(self.extend(self.comparison_piece, self.gapped_piece))
            self.max_score_alignments.append(Score(self.gapped_piece, extended_piece, self.gapped_bar_num - 1))
            for i in range(gapped_length - compare_length):
                extended_piece = self.shift(extended_piece)
                self.max_score_alignments.append(
                    Score(self.gapped_piece, extended_piece, self.gapped_bar_num - 1))
        elif gapped_length < compare_length:
            extended_piece = copy.deepcopy(self.extend(self.gapped_piece, self.comparison_piece))
            self.max_score_alignments.append(Score(extended_piece, self.comparison_piece, self.gapped_bar_num - 1))
            print ""
            for i in range(compare_length - gapped_length):
                extended_piece = self.shift(extended_piece)
                self.max_score_alignments.append(
                    Score(extended_piece, self.comparison_piece, self.gapped_bar_num - 1 + i))

    @staticmethod
    def extend(shorter, longer):
        difference = len(longer) - len(shorter)
        extended_arr = [''] * difference
        return shorter + extended_arr

    @staticmethod
    def shift(piece):
        swap = piece.pop()
        piece = [swap] + piece
        return piece


class Score:
    alignment_score = -1
    replacing_arr_index = 0
    actual_replaced_bar_num = 0
    replaced_bar = '    '
    adjust_index = -1
    comparison_obj = None

    def __init__(self, gapped, comparison, adjust):
        self.replaced_bar = comparison[adjust]
        self.alignment_score = self.get_alignment_score(gapped, comparison)
        print "Alignment Score: ", self.alignment_score
        print "Replaced Bar: ", self.replaced_bar

    # def _get_replaced_bar_num(self):
    #     number = self.replacing_arr_index - self.comparison_obj.left_shift + 1
    #     return number

    @staticmethod
    def get_alignment_score(gapped, comparison):
        # match score; if seq1(i) == seq2(i)
        # mismatch score; if seq1(i) != seq2(i)
        score = 0

        for i in range(len(gapped)):
            if gapped[i] == comparison[i]:
                score += 1

        return score

    def get_edit_distance(self, gapped, comparison):
        n = len(gapped)
        m = len(comparison)

        distance = [[0 for i in range(m + 1)] for j in range(n + 1)]

        for i in range(1, n + 1):
            distance[i][0] = distance[i - 1][0] + self._insert_cost(gapped[i - 1])

        for j in range(1, m + 1):
            distance[0][j] = distance[0][j - 1] + self._delete_cost(comparison[j - 1])

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                distance[i][j] = min(distance[i - 1][j] + 1,
                                     distance[i][j - 1] + 1,
                                     distance[i - 1][j - 1] + self._subst_cost(comparison[j - 1], gapped[i - 1]))
        return distance[n][m]

    @staticmethod
    def _subst_cost(x, y):
        if x == y:
            return 0
        else:
            return 2

    @staticmethod
    def _insert_cost(self, x):
        return 1

    @staticmethod
    def _delete_cost(self, x):
        return 1


class Corpus:
    old_corpus_file = ""
    new_corpus_file = ""
    database = []

    def __init__(self, old_file, new_file):
        self.old_corpus_file = old_file
        self.new_corpus_file = new_file

    def fill_database(self):
        with open(self.new_corpus_file) as corpus:
            for path in corpus:
                path = path.rstrip()
                self.database.append(musicXML_parsing.MusicXMLParsing(path))

    def list_dir(self):
        old_corpus = open(self.old_corpus_file, "w")
        for file in os.listdir("../musicXML/palestrina"):
            if file.endswith(".krn") or file.endswith(".xml"):
                old_corpus.write("../musicXML/palestrina/" + file + "\n")
        old_corpus.close()

    def clean(self):
        new_corpus = open(self.new_corpus_file, "w")
        line_num = 0
        with open(self.old_corpus_file) as corpus:
            for path in corpus:
                line_num += 1
                path = path.rstrip()
                print 'parsing line ', line_num
                try:
                    musicXML_parsing.MusicXMLParsing(path)
                    new_corpus.write(path + "\n")
                except AttributeError:
                    print '%s is a bad score', path
                except music21.exceptions21.StreamException:
                    print '%s is a not 4/4', path
                print 'Parsed', path

        new_corpus.close()


def main():
    # database = Corpus("path-list.txt", "parsable-path-list.txt")
    # database.fill_database()

    ground_truth = musicXML_parsing.MusicXMLParsing(
        '../musicXML/palestrina/Agnus-Dei-1_Palestrina-Giovanni-Pierluigi-da_file1.krn')
    compare = musicXML_parsing.MusicXMLParsing(
        '../musicXML/palestrina/Agnus-Dei-2_Palestrina-Giovanni-Pierluigi-da_file1.krn')
    # ground_truth = musicXML_parsing.MusicXMLParsing('../musicXML/tests/twinkle-twinkle.xml')
    # compare = musicXML_parsing.MusicXMLParsing('../musicXML/tests/test1.xml')

    # print ground_truth.rhythm_hash
    # print compare.rhythm_hash

    align = SimpleAlignment(ground_truth, compare, 'rhythm', 3)
    # print 'edit distance: ', align.min_edit_obj.alignment_score
    print 'replaced bar: ', align.max_score_obj.replaced_bar


main()
