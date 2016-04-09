import datetime
import copy
import time
import os
import simple_alignments
import musicXML_parsing


class Experimenter:
    corpus_path = ""
    output_file_path = ""
    mode = ""
    gapped_bar_num = 0

    def __init__(self, file_path, experiment_name, bar, mode):
        self.gapped_bar_num = bar
        self.corpus_path = file_path
        self.mode = mode
        self.output_file_path = "../results/" + self.create_output_file(experiment_name)

    def run_simple_alignment(self):
        piece_list = open(self.corpus_path, "r")
        first_line = piece_list.readline()
        first_line = first_line.rstrip()
        piece_list.close()
        ground_truth = musicXML_parsing.MusicXMLParsing(first_line)
        alignments = []
        with open(self.corpus_path) as corpus:
            for path in corpus:
                # i += 1
                # print "Path", path
                # print "First line", first_line
                path = path.rstrip()
                if path != first_line:
                    piece = musicXML_parsing.MusicXMLParsing(path)
                    alignments.append(
                        simple_alignments.SimpleAlignment(ground_truth, piece, self.mode, self.gapped_bar_num))
                else:
                    print "Does this happen?"
        max_alignment = self.get_max_score_alignment(alignments)
        print max_alignment.max_score_obj.replaced_bar

        naive_result = copy.deepcopy(ground_truth)
        naive_result.fill_gap(self.gapped_bar_num, max_alignment.max_score_obj.replaced_bar, self.mode)
        result = self.get_edit_distance(ground_truth, naive_result)
        self.write_output_file(ground_truth, naive_result, result)

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

    def write_output_file(self, ground, similar_piece, result):
        string = ""
        print "Piece Name: ", ground.name
        string += "\n"
        print "Missing Bar Number: ", self.gapped_bar_num
        print "\n--\nRESUlTS\n--\n"
        print ground.name
        string += "\n"
        print ground.rhythm_hash
        string += "\n"
        print similar_piece.name
        string += "\n"
        print similar_piece.rhythm_hash
        print "\nEdit Distance: ", result
        print "\nActual Bar: ", ground.rhythm_hash[self.gapped_bar_num - 1]
        print "\nReplaced Bar: ", similar_piece.rhythm_hash[self.gapped_bar_num - 1]
        # print string

    @staticmethod
    def get_max_score_alignment(all_alignments):
        max_score = all_alignments[0].alignment_score
        best_alignment = all_alignments[0]
        for obj in all_alignments:
            if obj.alignment_score > max_score:
                max_score = obj.alignment_score
                best_alignment = obj
        return best_alignment

    @staticmethod
    def create_output_file(name):
        time = datetime.datetime.now().time()
        filename = time.strftime("%Y-%m-%d %H:%M:%S") + name
        return filename


def main():
    result = Experimenter("../corpus/parsable-path-list-short.txt", "simple-alignment", 2, "rhythm")
    result.run_simple_alignment()


main()
