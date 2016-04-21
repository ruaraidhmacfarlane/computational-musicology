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
    result_parse = None

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
        comparison = self.alignments[0].comparison_parse
        for align in self.alignments:
            if self.scoring_method == 0:
                # max score
                if align.alignment_metric_result > metric:
                    metric = align.alignment_metric_result
                    replaced_bar = align.alignment_replaced_bar
                    comparison = align.comparison_parse
            elif self.scoring_method == 1:
                # min distance
                if align.metric < metric:
                    metric = align.alignment_metric_result
                    replaced_bar = align.alignment_replaced_bar
                    comparison = align.comparison_parse

        self.experiment_metric_result = metric
        self.experiment_replaced_bar = replaced_bar
        self.result_parse = comparison

    def create_result(self):
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
        overview.write(4, 0, "RESULTS", header)

        overview.write(5, 1, self.ground_truth.name)
        overview.write(6, 1, self.result_parse.name)

        max_length = max(self.ground_truth.length, self.result_parse.length)
        # total_dist = 0
        for i in range(max_length):
            if i >= self.ground_truth.length - 1:
                overview.write(6, i + 2, self.result_parse.feature[i])
                # overview.write(6, i + 2, str(self.get_edit_distance("", comp_feat[i])))
                # total_dist += self.get_edit_distance("", comp_feat[i])
            elif i >= self.result_parse.length - 1:
                overview.write(5, i + 2, self.ground_truth.feature[i])
                # overview.write(6, i + 2, str(self.get_edit_distance(ground.rhythm_hash[i], "")))
                # total_dist += self.get_edit_distance(ground.rhythm_hash[i], "")
            else:
                overview.write(5, i + 2, self.ground_truth.feature[i])
                overview.write(6, i + 2, self.result_parse.feature[i])
                # if ground.rhythm_hash[i] == comp_feat[i]:
                #     overview.write(4, i + 2, ground.rhythm_hash[i], highlight_match)
                #     overview.write(5, i + 2, comp_feat[i], highlight_match)
                # else:
                #     overview.write(5, i + 2, ground.rhythm_hash[i])
                #     overview.write(6, i + 2, comp_feat[i])
            #     overview.write(6, i + 2, str(self.get_edit_distance(ground.rhythm_hash[i], comp_feat[i])))
            #     total_dist += self.get_edit_distance(ground.rhythm_hash[i], comp_feat[i])
            # overview.write(7, i + 2, str(total_dist))

        overview.write(8, 0, "Metric: ", header)
        overview.write(9, 0, "Edit Distance: ", header)
        overview.write(10, 0, "Actual Bar: ", header)
        overview.write(11, 0, "Replaced Bar: ", header)
        overview.write(8, 1, str(self.experiment_metric_result))
        overview.write(9, 1, str(self.experiment_dist_result))
        overview.write(10, 1, self.ground_truth.previous_feature_bar)
        overview.write(11, 1, self.experiment_replaced_bar)

        # num_correct = 0

        for n, alignment in enumerate(self.alignments):
            row = 0
            wb.add_sheet(alignment.comparison_parse.name)
            piece_sheet = wb.get_sheet(n + 1)

            shift_num = 0

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
                    piece_sheet.write(row + 2, i + 2, score.comparison_feat[i])


                # for i in range(len(score.gapped_feat)):
                #     piece_sheet.write(row + 1, i + 2, score.gapped_feat[i])
                # for i in range(len(score.comparison_feat)):
                #     piece_sheet.write(row + 2, i + 2, score.comparison_feat[i])

                piece_sheet.write(row + 5, 1, "Score")
                piece_sheet.write(row + 6, 1, "Replaced Bar")
                piece_sheet.write(row + 7, 1, "Result Edit Distance")
                piece_sheet.write(row + 5, 2, str(score.metric))
                piece_sheet.write(row + 6, 2, score.replaced_bar_feat)
                scorer = simple_alignments.Scorer(self.ground_truth.previous_feature_bar, score.replaced_bar_feat)
                result = scorer.edit_distance()
                piece_sheet.write(row + 7, 2, str(result))
                shift_num += 1
                row += 10

        wb.save(path + "/result.xls")

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
