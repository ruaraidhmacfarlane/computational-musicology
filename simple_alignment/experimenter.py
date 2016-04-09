import datetime
import copy
import time
import os
import simple_alignments
import musicXML_parsing


class Experimenter:
    corpus_path = ""
    output_file_path = ""
    gapped_bar_num = 0

    def __init__(self, file_path, experiment_name, bar):
        self.gapped_bar_num = bar
        self.corpus_path = file_path
        self.output_file_path = "../results/" + self.create_output_file(experiment_name)

    def run_simple_alignment(self):
        piece_list = open(self.corpus_path, "r")
        first_line = piece_list.readline()
        first_line = first_line.rstrip()
        piece_list.close()
        ground_truth = musicXML_parsing.MusicXMLParsing(first_line)
        alignments = []
        # i = 0
        # start_time = time.time()
        with open(self.corpus_path) as corpus:
            for path in corpus:
                # i += 1
                if path != first_line:
                    path = path.rstrip()
                    piece = musicXML_parsing.MusicXMLParsing(path)
                    alignments.append(simple_alignments.SimpleAlignment(ground_truth, piece, "rhythm", self.gapped_bar_num))
                # now_time = time.time()
                # time_left = (now_time - start_time) * (len(self.corpus) - i)
                # print time_left
        max_alignment = self.get_max_score_alignment(alignments)
        naive_result = copy.deepcopy(ground_truth)
        naive_result[self.gapped_bar_num - 1] = max_alignment.replaced_bar
        result = self.get_edit_distance(ground_truth, naive_result)
        self.write_output_file(ground_truth, naive_result, result)


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

    def write_output_file(self, ground, similar_piece, result):
        string = ""
        string += "Piece Name: ", ground.name
        string += "\n"
        string += "Missing Bar Number: ", self.gapped_bar_num
        string += "\n\n--\nRESUlTS\n--\n"
        string += ground.name
        string += "\n"
        string += ground.rhythm_hash
        string += "\n"
        string += similar_piece.name
        string += "\n"
        string += similar_piece.rhythm_hash
        string += "\nEdit Distance: ", result
        string += "\nActual Bar: ", ground.rhythm_hash[self.gapped_bar_num - 1]
        string += "\nReplaced Bar: ", similar_piece.rhythm_hash[self.gapped_bar_num - 1]
        print string


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
    result = Experimenter("../corpus/parsable-path-list.txt", "simple-alignment", 2)
    result.run_simple_alignment()
main()
