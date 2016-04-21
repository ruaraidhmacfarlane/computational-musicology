import numpy
import datetime
import simple_alignments
import musicXML_parsing
import os
import xlwt


class Experimenter:
    corpus_path = ""
    mode = ""
    scoring_method = -1
    gapped_bar_num = 0

    alignments = []

    ground_truth_path = ""
    ground_truth = None

    experiment_metric_result = 0
    experiment_replaced_bar = ""
    experiment_dist_result = 0

    def __init__(self, file_path, bar, mode, method):
        self.corpus_path = file_path
        self.mode = mode
        self.scoring_method = method
        self.gapped_bar_num = bar

        piece_list = open(self.corpus_path, "r")
        path = piece_list.readline()
        self.ground_truth_path = path.rstrip()
        piece_list.close()

        self.alignments = []

        self.ground_truth = musicXML_parsing.MusicXMLParsing(self.ground_truth_path, self.mode)
        self.ground_truth.create_gap(self.gapped_bar_num)

        self.experiment_metric_result = 0
        self.experiment_replaced_bar = ""
        self.experiment_dist_result = 0

    def run_alignments(self):
        with open(self.corpus_path) as corpus:
            for path in corpus:
                path = path.rstrip()
                if path != self.ground_truth_path:
                    comparison_piece = musicXML_parsing.MusicXMLParsing(path, self.mode)
                    align = simple_alignments.SimpleAlignment(self.ground_truth, comparison_piece, self.scoring_method)
                    self.alignments.append(align)

        self.set_replacement_scorings()
        scorer = simple_alignments.Scorer(self.ground_truth.previous_feature_bar, self.experiment_replaced_bar)
        edit_dist_result = scorer.edit_distance()
        self.experiment_dist_result = edit_dist_result

        self.create_result()

    def set_replacement_scorings(self):
        metric = self.alignments[0].alignment_metric_result
        replaced_bar = self.alignments[0].alignment_replaced_bar

        for align in self.alignments:
            if self.scoring_method == 0:
                # max score
                if align.alignment_metric_result > metric:
                    metric = align.alignment_metric_result
                    replaced_bar = align.alignment_replaced_bar
            elif self.scoring_method == 1:
                # min distance
                if align.metric < metric:
                    metric = align.alignment_metric_result
                    replaced_bar = align.alignment_replaced_bar

        self.alignment_metric_result = metric
        self.alignment_replaced_bar = replaced_bar

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
        filename = "%s-%s-%s" % (time.day, time.month, time.year) + "_%s-%s-%s" % (
        time.hour, time.minute, time.second) + "_" + name
        return filename

    def is_duplicate(self):
        # you should get all the pieces parsed for rhyhtm then just perform the edit distance on all of them
        # new_corpus = open("../corpus/duplicate-list.txt", "w")
        with open(self.corpus_path) as corpus:
            for path_i in corpus:
                path_i = path_i.rstrip()
                parsed_i = musicXML_parsing.MusicXMLParsing(path_i)
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

    # def create_result(self, ground, similar_piece, all_alignments, comp_name, comp_feat, alignment_score, result):
    def create_result(self, alignments):
        if self.scoring_method == 0:
            meth = "simple"
        elif self.scoring_method == 1:
            meth = "edit"
        dir_name = self.ground_truth.name + "_" + self.mode + "_" + meth + "_" + str(self.ground_truth.gapped_bar_num)
        path = "../results/" + dir_name
        if not os.path.exists(path):
            os.makedirs(path)

        header = xlwt.easyxf('font: name Arial, color-index black, bold on')
        highlight_match = xlwt.easyxf('font: name Arial, color-index red')

        wb = xlwt.Workbook()
        wb.add_sheet('Overview')
        overview = wb.get_sheet(0)
        overview.write(0, 0, "Analysing Mass:", header)
        overview.write(1, 0, "Missing Bar Number:", header)
        overview.write(2, 0, "Missing Bar:", header)
        overview.write(0, 1, self.ground_truth.name)
        overview.write(1, 1, str(self.ground_truth.gapped_bar_num))
        overview.write(2, 1, self.ground_truth.previous_feature_bar)

        # overview.write(3, 0, "Gold Standard", header)
        # overview.write(6, 0, "Taken From Piece", header)

        # overview.write(4, 0, "RESULTS", header)
        # overview.write(5, 1, ground.name)
        # overview.write(6, 1, comp_name)
        # # overview.write(6, 1, "Edit Distance:")
        # # overview.write(7, 1, "Aggregated Edit Distance")
        # max_length = max(len(ground.rhythm_hash), len(comp_feat))

        # total_dist = 0
        # for i in range(max_length):
        #     if i >= len(ground.rhythm_hash) - 1:
        #         overview.write(6, i + 2, comp_feat[i])
        #         # overview.write(6, i + 2, str(self.get_edit_distance("", comp_feat[i])))
        #         # total_dist += self.get_edit_distance("", comp_feat[i])
        #     elif i >= len(comp_feat) - 1:
        #         overview.write(5, i + 2, ground.rhythm_hash[i])
        #         # overview.write(6, i + 2, str(self.get_edit_distance(ground.rhythm_hash[i], "")))
        #         # total_dist += self.get_edit_distance(ground.rhythm_hash[i], "")
        #     else:
        #         # if ground.rhythm_hash[i] == comp_feat[i]:
        #         #     overview.write(4, i + 2, ground.rhythm_hash[i], highlight_match)
        #         #     overview.write(5, i + 2, comp_feat[i], highlight_match)
        #         # else:
        #             overview.write(5, i + 2, ground.rhythm_hash[i])
        #             overview.write(6, i + 2, comp_feat[i])
        #     #     overview.write(6, i + 2, str(self.get_edit_distance(ground.rhythm_hash[i], comp_feat[i])))
        #     #     total_dist += self.get_edit_distance(ground.rhythm_hash[i], comp_feat[i])
        #     # overview.write(7, i + 2, str(total_dist))
        #
        # overview.write(8, 0, "Alignment Score: ", header)
        # overview.write(9, 0, "Edit Distance: ", header)
        # overview.write(10, 0, "Actual Bar: ", header)
        # overview.write(11, 0, "Replaced Bar: ", header)
        # overview.write(8, 1, str(alignment_score))
        # overview.write(9, 1, str(result))
        # overview.write(10, 1, ground.rhythm_hash[self.gapped_bar_num - 1])
        # overview.write(11, 1, similar_piece.rhythm_hash[self.gapped_bar_num - 1])

        # num_correct = 0
        # masses = []
        # for mass in all_alignments:
        #     masses.append(mass)
        #
        for n, alignment in enumerate(alignments):
            row = 0
            wb.add_sheet(alignment.comparison_parse.name)
            piece_sheet = wb.get_sheet(n + 1)
        #     # piece_sheet.write(0, 0, outer_obj.comparison_name)
        #     # for i in range(len(outer_obj.comparison_parse.rhythm_hash)):
        #     #     piece_sheet.write(1, i + 2, outer_obj.comparison_parse.rhythm_hash[i])
            shift_num = 0
        #     # print len(outer_obj.max_score_alignments)
            for score in alignment.scores:
        #         # print n + shift_num
        #         # if '' != inner_obj.replaced_bar:
        #         num_correct += 1
                piece_sheet.write(row, 0, "Shift")
                piece_sheet.write(row, 1, str(shift_num))
                piece_sheet.write(row + 1, 1, alignment.gapped_parse.name)
                piece_sheet.write(row + 2, 1, alignment.comparison_parse.name)
                for i in range(len(score.gapped_feat)):
                    piece_sheet.write(row + 1, i + 2, score.gapped_feat[i])
                for i in range(len(score.comparison_feat)):
                    piece_sheet.write(row + 2, i + 2, score.comparison_feat[i])
                # piece_sheet.write(row + 3, 1, "Score")
                # piece_sheet.write(row + 4, 1, "Replaced Bar")
                # piece_sheet.write(row + 5, 1, "Edit Distance")
                # piece_sheet.write(row + 3, 2, str(inner_obj.alignment_score))
                # piece_sheet.write(row + 4, 2, inner_obj.replaced_bar)
                # result = self.get_edit_distance(self.gapped_bar, inner_obj.replaced_bar)
                # piece_sheet.write(row + 5, 2, str(result))
        #         #         #             if shift_num == 0 or shift_num == 8:
        #         #         #                 print "TO CSV"
        #         #         #                 print "   ", inner_obj.gapped_piece_feat
        #         #         #                 print "   ", inner_obj.target_piece_feat
        #         #         #             print "    Score = ", inner_obj.alignment_score
        #         #         #             print "    Replaced Bar = ", inner_obj.replaced_bar
        #         #         #             print "    Edit Distance = ", result
                shift_num += 1
                row += 4

        # print "Returned %s results" % num_correct

        wb.save(path + "/result.xls")

    def get_alignment_distance(self, gapped, comparison):
        distance = 0
        for i in range(len(gapped)):
            distance += self.get_align_distance(gapped[i], comparison[i])
        return distance

    def write_exp_info(self, ground):
        dir_name = ground.name + "_" + self.mode + "_" + self.gapped_bar_num
        os.makedirs("../results/" + dir_name)
        filename = self.output_file_path
        print filename
        print "Experiment Name: ", self.create_output_file(self.experiment_name)
        print "Piece Name: ", ground.name
        print "Missing Bar Number: ", self.gapped_bar_num
        print "Missing Bar: ", self.gapped_bar

    def write_all_alignment_score(self, all_alignments):
        num_correct = 0
        for outer_obj in all_alignments:
            print "Comparison Mass: ", outer_obj.comparison_name
            print outer_obj.comparison_parse.rhythm_hash
            shift_num = 0
            for inner_obj in outer_obj.max_score_alignments:
                if '' != inner_obj.replaced_bar:
                    num_correct += 1
                    print "  Shift: ", shift_num
                    if shift_num == 0 or shift_num == 8:
                        print "TO CSV"
                        print "   ", inner_obj.gapped_piece_feat
                        print "   ", inner_obj.target_piece_feat
                    print "    Score = ", inner_obj.alignment_score
                    print "    Replaced Bar = ", inner_obj.replaced_bar
                    result = self.get_edit_distance(self.gapped_bar, inner_obj.replaced_bar)
                    print "    Edit Distance = ", result
                shift_num += 1
        print "Returned %s results" % num_correct

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

    def print_exp_info(self, ground):
        filename = self.output_file_path
        print filename
        print "Experiment Name: ", self.create_output_file(self.experiment_name)
        print "Piece Name: ", ground.name
        print "Missing Bar Number: ", self.gapped_bar_num
        print "Missing Bar: ", self.gapped_bar

    def print_all_alignment_scores(self, all_alignments):
        print "----------"
        print "ALL SCORES"
        print "----------"
        num_correct = 0
        for outer_obj in all_alignments:
            print "Comparison Mass: ", outer_obj.comparison_name
            print outer_obj.comparison_parse.rhythm_hash
            shift_num = 0
            for inner_obj in outer_obj.max_score_alignments:
                if '' != inner_obj.replaced_bar:
                    num_correct += 1
                    print "  Shift: ", shift_num
                    if shift_num == 0 or shift_num == 8:
                        print "TO CSV"
                        print "   ", inner_obj.gapped_piece_feat
                        print "   ", inner_obj.target_piece_feat
                    print "    Score = ", inner_obj.alignment_score
                    print "    Replaced Bar = ", inner_obj.replaced_bar
                    result = self.get_edit_distance(self.gapped_bar, inner_obj.replaced_bar)
                    print "    Edit Distance = ", result
                shift_num += 1
        print "Returned %s results" % num_correct

    def print_output(self, ground, similar_piece, comp_name, comp_feat, alignment_score, result):
        print "\n-------\nRESUlTS\n-------\n"
        print "GOLD STANDARD: "
        print ground.rhythm_hash
        # # print ground.parsons_code
        # print "RESULTING PIECE: "
        # print similar_piece.rhythm_hash
        # print similar_piece.parsons_code
        print "TAKEN FROM PIECE: ", comp_name
        print comp_feat
        # print similar_piece.parsons_code
        print "\nAlignment Score: ", alignment_score
        print "Edit Distance: ", result
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
    result = Experimenter("../corpus/palestrina.txt", 2, "rhythm", 0)
    result.run_alignments()

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
