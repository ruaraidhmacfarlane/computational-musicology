import music21
import copy
import musicXML_parsing
import os


class SimpleAlignment:
    gapped_parse = None
    comparison_parse = None
    scoring_method = 1  # 0 Simple || 1 Edit Distance
    scores = []
    alignment_metric_result = 0
    alignment_replaced_bar = ""

    def __init__(self, gapped, comparison, scoring_method):
        self.gapped_parse = copy.deepcopy(gapped)
        self.comparison_parse = copy.deepcopy(comparison)
        self.scoring_method = scoring_method
        self.scores = []
        self.align()
        self.set_alignment_result()

    def align(self):
        gapped_length = self.gapped_parse.length
        compare_length = self.comparison_parse.length
        if gapped_length == compare_length:
            metric = Score(self.gapped_parse.feature, self.comparison_parse.feature,
                           self.gapped_parse.gapped_bar_num - 1, self.scoring_method)
            self.scores.append(metric)
        elif gapped_length > compare_length:
            extended_piece = self.extend(self.comparison_parse.feature, self.gapped_parse.feature)
            metric = Score(self.gapped_parse.feature, extended_piece, self.gapped_parse.gapped_bar_num - 1,
                           self.scoring_method)
            self.scores.append(metric)
            for i in range(gapped_length - compare_length):
                extended_piece = self.shift(extended_piece)
                metric = Score(self.gapped_parse.feature, extended_piece, self.gapped_parse.gapped_bar_num - 1,
                               self.scoring_method)
                self.scores.append(metric)
        elif gapped_length < compare_length:
            extended_piece = self.extend(self.gapped_parse.feature, self.comparison_parse.feature)
            metric = Score(extended_piece, self.comparison_parse.feature, self.gapped_parse.gapped_bar_num - 1,
                           self.scoring_method)
            self.scores.append(metric)
            for i in range(compare_length - gapped_length):
                extended_piece = self.shift(extended_piece)
                metric = Score(extended_piece, self.comparison_parse.feature, self.gapped_parse.gapped_bar_num - 1 + i,
                               self.scoring_method)
                self.scores.append(metric)

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

    def set_alignment_result(self):
        score_metric = self.scores[0].metric
        score_replaced_bar = self.scores[0].replaced_bar_feat
        for score in self.scores:
            if self.scoring_method == 0:
                # max score
                if score.metric > score_metric and score.replaced_bar_feat != "":
                    score_metric = score.metric
                    score_replaced_bar = score.replaced_bar_feat
            elif self.scoring_method == 1:
                # min distance
                if score.metric < score_metric and score.replaced_bar_feat != "":
                    score_metric = score.metric
                    score_replaced_bar = score.replaced_bar_feat
            if score_replaced_bar == "" and score.replaced_bar_feat != "":
                score_metric = score.metric
                score_replaced_bar = score.replaced_bar_feat

        self.alignment_metric_result = score_metric
        self.alignment_replaced_bar = score_replaced_bar


class Score:
    gapped_feat = []
    comparison_feat = []

    replaced_bar_feat = ""
    metric = -1

    def __init__(self, gapped_feat, comparison_feat, adjust, method):
        self.gapped_feat = gapped_feat
        self.comparison_feat = comparison_feat

        self.replaced_bar_feat = comparison_feat[adjust]

        self.metric = self.get_metric(self.gapped_feat, self.comparison_feat, method)


    @staticmethod
    def get_metric(gapped, comparison, method):
        metric = 0
        for i in range(len(gapped)):
            scorer = Scorer(gapped[i], comparison[i])
            if method == 0:
                metric += scorer.edit_distance()
            elif method == 1:
                metric += scorer.simple_score()
        return metric


class Scorer:
    match_score = 1
    x = ""
    y = ""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def simple_score(self):
        if self.x == self.y:
            return self.match_score

    def edit_distance(self):
        n = len(self.y)
        m = len(self.x)

        distance = [[0 for i in range(m + 1)] for j in range(n + 1)]

        for i in range(1, n + 1):
            distance[i][0] = distance[i - 1][0] + self._insert_cost(self.y[i - 1])

        for j in range(1, m + 1):
            distance[0][j] = distance[0][j - 1] + self._delete_cost(self.x[j - 1])

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                distance[i][j] = min(distance[i - 1][j] + 1,
                                     distance[i][j - 1] + 1,
                                     distance[i - 1][j - 1] + self._subst_cost(self.x[j - 1], self.y[i - 1]))
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


class Corpus:
    old_corpus_file = ""
    new_corpus_file = ""
    mode = -1
    database = []

    def __init__(self, old_file, new_file, mode):
        self.old_corpus_file = old_file
        self.new_corpus_file = new_file
        self.mode = mode

    def fill_database(self):
        with open(self.new_corpus_file) as corpus:
            for path in corpus:
                path = path.rstrip()
                self.database.append(musicXML_parsing.MusicXMLParsing(path, self.mode))

    def list_dir(self):
        old_corpus = open(self.old_corpus_file, "w")
        path = "../musicXML/palestrina/Humdrum"
        for dir in os.listdir(path):
            for file in os.listdir(path + "/" + dir):
                if file.endswith(".krn") or file.endswith(".xml") or file.endswith(".mid"):
                    old_corpus.write("../musicXML/palestrina/Humdrum/" + dir + "/" + file + "\n")
        old_corpus.close()

    def clean(self):
        new_corpus = open(self.new_corpus_file, "w")
        line_num = 0
        with open(self.old_corpus_file) as corpus:
            for path in corpus:
                line_num += 1
                path = path.rstrip()
                print 'Line: ', line_num
                try:
                    musicXML_parsing.MusicXMLParsing(path, self.mode)
                    new_corpus.write(path + "\n")
                    print 'Parsed', path
                except AttributeError:
                    print '%s is a bad score' % path
                except music21.exceptions21.StreamException:
                    print '%s is a not 4/4' % path
        new_corpus.close()
