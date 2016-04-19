import copy
import numpy
import datetime
import simple_alignments
import musicXML_parsing
import music21


class Experimenter:
    corpus_path = ""
    output_file_path = ""
    mode = ""
    gapped_bar_num = 0

    def __init__(self, file_path, experiment_name, bar, mode):
        self.gapped_bar_num = bar
        self.corpus_path = file_path
        self.mode = mode
        self.output_file_path = "../results/" + self.create_output_file(experiment_name) + ".txt"
        self.experiment_name = experiment_name

    def run_simple_alignment(self):
        piece_list = open(self.corpus_path, "r")
        first_line = piece_list.readline()
        first_line = first_line.rstrip()
        piece_list.close()
        ground_truth = musicXML_parsing.MusicXMLParsing(first_line)
        gapped = copy.deepcopy(ground_truth)
        alignments = []
        with open(self.corpus_path) as corpus:
            for path in corpus:
                path = path.rstrip()
                if path != first_line:
                    piece = musicXML_parsing.MusicXMLParsing(path)
                    alignments.append(simple_alignments.SimpleAlignment(gapped, piece, self.mode, self.gapped_bar_num))
        max_alignment = self.get_max_score_alignment(alignments)
        # print "#### max alignment ", max_alignment
        naive_result = copy.deepcopy(ground_truth)
        naive_result.fill_gap(self.gapped_bar_num, max_alignment.replaced_bar, self.mode)
        result = self.get_edit_distance(ground_truth, naive_result)
        # self.write_output_file(ground_truth, naive_result, max_alignment.comparison_parse, result)
        self.print_output(ground_truth, naive_result, result)

    def get_edit_distance(self, gapped_parse, comparison_parse):
        if self.mode == "rhythm":
            gapped = gapped_parse.rhythm_hash
            comparison = comparison_parse.rhythm_hash
        elif self.mode == "parson":
            gapped = gapped_parse.parsons_code
            comparison = comparison_parse.parsons_code
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

        max_value = numpy.amax(distance)
        percentage = ((max_value - distance[n][m]) / max_value) * 100
        # return percentage
        return distance[n][m]

    @staticmethod
    def _subst_cost(x, y):
        if x == y:
            return 0
        else:
            return 2

    @staticmethod
    def _insert_cost(x):
        return 1

    @staticmethod
    def _delete_cost(x):
        return 1

    @staticmethod
    def get_max_score_alignment(all_alignments):
        min_dist = all_alignments[0].max_score_alignments[0].alignment_score
        best_alignment = all_alignments[0].max_score_alignments[0]
        for outer_obj in all_alignments:
            for inner_obj in outer_obj.max_score_alignments:
                if inner_obj.alignment_score < min_dist and inner_obj.replaced_bar != '':
                    min_dist = inner_obj.alignment_score
                    best_alignment = inner_obj
        return best_alignment

    @staticmethod
    def create_output_file(name):
        time = datetime.datetime.now()
        filename = "%s-%s-%s" % (time.day, time.month, time.year) + "_%s-%s-%s" % (time.hour, time.minute, time.second) + "_" + name
        return filename

    def is_duplicate(self):
        # you should get all the pieces parsed for rhyhtm then just perform the edit distance on all of them
        # new_corpus = open("../corpus/duplicate-list.txt", "w")
        with open(self.corpus_path) as corpus:
            for path_i in corpus:
                path_i = path_i.rstrip()
                parsed_i =  musicXML_parsing.MusicXMLParsing(path_i)
                for path_j in corpus:
                    path_j = path_j.rstrip()
                    if path_i != path_j:
                        parsed_j = musicXML_parsing.MusicXMLParsing(path_j)
                        difference = self.get_edit_distance(parsed_i, parsed_j)
                        if difference == 0:
                            # print "%s is the same as %s" % (parsed_i.name, parsed_j.name)
                            print path_j
                            # new_corpus.write(path_j + "\n")
                        # else:
                        #     print "--"
                            # print "%s is different from %s" % (parsed_i.name, parsed_j.name)
        # new_corpus.close()

    def write_output_file(self, ground, similar_piece, result):
        filename = self.output_file_path
        f = open(filename, 'w')
        f.write("Experiment Name: " + self.create_output_file(self.experiment_name) + "\n")
        f.write("Piece Name: " + ground.name + "\n")
        f.write("Missing Bar Number: " + str(self.gapped_bar_num) + "\n")
        f.write("\n-------\nRESUlTS\n-------\n")
        f.write("GOLD STANDARD: " + "\n")
        f.write("[" + ", ".join(ground.rhythm_hash) + "]" + "\n\n")
        f.write("RESULTING PIECE: " + "\n")
        f.write("[" + ", ".join(similar_piece.rhythm_hash) + "]" + "\n\n")
        # f.write("TAKEN FROM PIECE: " + aligned_piece.name + "\n")
        # f.write("[" + ", ".join(aligned_piece.rhythm_hash) + "]" + "\n\n")
        f.write("\nEdit Distance: " + str(result) + "%\n")
        f.write("Actual Bar: " + ground.rhythm_hash[self.gapped_bar_num - 1] + "\n")
        f.write("Replaced Bar: " + similar_piece.rhythm_hash[self.gapped_bar_num - 1] + "\n")
        f.close()

    def print_output(self, ground, similar_piece, result):
        filename = self.output_file_path
        print filename
        print "Experiment Name: ", self.create_output_file(self.experiment_name)
        print "Piece Name: ", ground.name
        print "Missing Bar Number: ", self.gapped_bar_num
        print "\n-------\nRESUlTS\n-------\n"
        print "GOLD STANDARD: "
        print ground.rhythm_hash
        # print ground.parsons_code
        print "RESULTING PIECE: "
        print similar_piece.rhythm_hash
        # print similar_piece.parsons_code
        # print "TAKEN FROM PIECE: ", aligned_piece.name
        # print aligned_piece.rhythm_hash
        # print similar_piece.parsons_code
        print "\nEdit Distance: ", result
        print "Actual Bar: ", ground.rhythm_hash[self.gapped_bar_num - 1]
        # print "Actual Bar: ", ground.parsons_code[self.gapped_bar_num - 1]
        print "Replaced Bar: ", similar_piece.rhythm_hash[self.gapped_bar_num - 1]
        # print "Replaced Bar: ", similar_piece.parsons_code[self.gapped_bar_num - 1]


class Evaluator:
    piece_x = None
    piece_y = None
    edit_distance = 0

    def __init__(self, piece_x, piece_y):
        self.piece_x = piece_x
        self.piece_y = piece_y
        self.edit_distance = self.get_edit_distance()

        print piece_x
        print piece_y
        print "Edit Distance: ", self.edit_distance

    def get_edit_distance(self):
        gapped = self.piece_x[0]
        comparison = self.piece_y[0]
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

        max_value = numpy.amax(distance)
        percentage = ((max_value - distance[n][m]) / max_value) * 100
        # return percentage
        # print distance
        return distance[n][m]

    @staticmethod
    def _subst_cost(x, y):
        if x == y:
            return 0
        else:
            return 2

    @staticmethod
    def _insert_cost(x):
        return 1

    @staticmethod
    def _delete_cost(x):
        return 1

def main():
    result = Experimenter("../corpus/palestrina.txt", "simple-alignment-rhythm", 2, "rhythm")
    result.run_simple_alignment()
    # result.is_duplicate()
    # result = Experimenter("../corpus/parsable-path-list-short.txt", "simple-alignment-parson", 2, "parson")
    # result.run_simple_alignment()

    # db = simple_alignments.Corpus("../corpus/palestrina-path-list-v2.txt", "../corpus/palestrina.txt")
    # db.list_dir()
    # db.clean()

    # print x.rhythm_hash
    # print y.rhythm_hash
    # test = simple_alignments.SimpleAlignment(x,y,"rhythm",2)
    # print test.alignment_score
    # x = musicXML_parsing.MusicXMLParsing("../musicXML/palestrina/Agnus-Dei-1_Palestrina-Giovanni-Pierluigi-da_file1.krn")
main()
