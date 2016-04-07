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
    right_shift = 0
    left_shift = 0

    def __init__(self, gapped, comparison, feat):
        self.attr = feat
        self.gapped_parse = gapped
        self.comparison_parse = comparison
        self.gapped_bar_num = gapped.gapped_bar_num

        if self.attr == 'parson':
            self.gapped_piece = copy.deepcopy(self.gapped_parse).parsons_code
            self.comparison_piece = copy.deepcopy(self.comparison_parse).parsons_code
        elif self.attr == 'rhythm':
            self.gapped_piece = copy.deepcopy(self.gapped_parse).rhythm_hash
            self.comparison_piece = copy.deepcopy(self.comparison_parse).rhythm_hash

        self.base_align()
        self.get_min_edit_obj()

    def get_min_edit_obj(self):
        min_obj = self.min_edit_alignments[0]
        minimum_edit = min_obj.edit_distance

        for i in self.min_edit_alignments:
            if i.edit_distance < minimum_edit:
                minimum_edit = i.edit_distance
                min_obj = i
        self.min_edit_obj = min_obj

    def base_align(self):
        gapped_length = len(self.gapped_piece)
        compare_length = len(self.comparison_piece)

        if gapped_length == compare_length:
            self.min_edit_alignments.append(EditDistance(self.gapped_piece, self.comparison_piece, self.gapped_bar_num - 1))
        # elif gapped_length > compare_length:
        #     self.comparison_piece = self.extend(self.comparison_piece, self.gapped_piece)
        #     self.min_edit_alignments = EditDistance(self.gapped_piece, self.comparison_piece, self.gapped_bar_num - 1)
        #     for i in range(gapped_length - 1):
        #         self.comparison_piece = copy.deepcopy(self.shift(extended_piece))
        #         self.min_edit_alignments.append(
        #             EditDistance(self.gapped_piece, self.comparison_piece, self.gapped_bar_num - 1))
        # elif gapped_length < compare_length:
        #     self.gapped_piece = self.extend(self.gapped_piece, self.comparison_piece)
        #     self.min_edit_alignments = EditDistance(self.gapped_piece, self.comparison_piece, self.gapped_bar_num - 1)
        #     for i in range(gapped_length - 1):
        #         self.gapped_piece = copy.deepcopy(self.shift(extended_piece))

    self.min_edit_alignments.append(EditDistance(self.gapped_piece, self.comparison_piece, self.gapped_bar_num - 1))

    def extend(self, shorter, longer):
        difference = len(longer) - len(shorter)
        extended_arr = ['    '] * difference
        return shorter + extended_arr




class EditDistance:
    edit_distance = -1
    replacing_arr_index = 0
    actual_replaced_bar_num = 0
    replaced_bar = '    '
    adjust_index = -1
    comparison_obj = None

    def __init__(self, gapped, comparison, adjust):
        self.replaced_bar = comparison[adjust]
        self.edit_distance = self.get_edit_distance(gapped, comparison)
    # def _get_replaced_bar_num(self):
    #     number = self.replacing_arr_index - self.comparison_obj.left_shift + 1
    #     return number

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

    def _subst_cost(self, x, y):
        if x == y:
            return 0
        else:
            return 2

    def _insert_cost(self, x):
        return 1

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

    ground_truth = musicXML_parsing.MusicXMLParsing('../musicXML/tests/rhythm-test.xml')
    compare = musicXML_parsing.MusicXMLParsing('../musicXML/tests/rhythm-test.xml')
    ground_truth.create_gap(3)
    align = SimpleAlignment(ground_truth, compare, 'rhythm')
    print 'edit distance: ', align.min_edit_obj.edit_distance
    print 'replaced bar: ', align.min_edit_obj.replaced_bar
# print 'replaced bar number: ', align.min_edit_obj.actual_replaced_bar_num

main()
