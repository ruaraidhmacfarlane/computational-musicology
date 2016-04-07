import music21, copy, musicXML_parsing, os

class SimpleAlignment:

	# parson || rhythm
	attr = ''
	gapped_parse = None
	comparison_parse = None
	gapped_extended_piece = []
	comparison_extended_piece = []
	extended_length = 0
	min_edit_alignments = []
	min_edit_obj = None
	right_shift = 0
	left_shift = 0

	def __init__(self, gapped, comparison, attr):
		self.attr = attr
		self.gapped_parse = gapped
		self.comparison_parse = comparison
		self.extended_length = gapped.length + comparison.length
		self.align()
		self.get_min_edit_obj()

	def get_min_edit_obj(self):
		minimum_edit = self.min_edit_alignments[0].edit_distance
		min_obj = None
		for i in self.min_edit_alignments:
			if i.edit_distance < minimum_edit:
				minimum_edit = i.edit_distance
				min_obj = i
		self.min_edit_obj = min_obj

	def align(self):
		self.extend()
		self.create_gap()
		print self.gapped_extended_piece
		print self.comparison_extended_piece
		for i in range(self.extended_length):
			self.min_edit_alignments.append(EditDistance(i, self))
			self.adjust(i)
			# print self.gapped_extended_piece
			# print self.comparison_extended_piece


	def extend(self):
		a = [''] * self.gapped_parse.length
		b = [''] * self.comparison_parse.length
		self.left_shift = len(b)
		if self.attr == 'parson':
			self.gapped_extended_piece = copy.deepcopy(self.gapped_parse).parsons_code + a
			self.comparison_extended_piece = b + copy.deepcopy(self.comparison_parse).parsons_code
		elif self.attr == 'rhythm':
			self.gapped_extended_piece = copy.deepcopy(self.gapped_parse).rhythm_hash + a
			self.comparison_extended_piece = b + copy.deepcopy(self.comparison_parse).rhythm_hash

	def create_gap(self):
		self.gapped_extended_piece.pop(self.gapped_parse.gapped_bar_num - 1)
		self.gapped_extended_piece.append('')

	def adjust(self, adjust_index):
		if adjust_index % 2 == 0:
			swap = self.gapped_extended_piece.pop()
			self.gapped_extended_piece = [swap] + self.gapped_extended_piece
			self.right_shift += 1
		else:
			swap = self.comparison_extended_piece.pop(0)
			self.comparison_extended_piece = self.comparison_extended_piece + [swap]
			self.left_shift -= 1

class EditDistance:

	edit_distance = -1
	replacing_arr_index = 0
	actual_replaced_bar_num = 0
	replaced_bar = '    '
	adjust_index = -1
	comparison_obj = None

	def __init__(self, index, comparison_obj):
		self.adjust_index = index
		self.comparison_obj = copy.deepcopy(comparison_obj)
		if self.adjust_index % 2 == 0:
			self.replacing_arr_index = comparison_obj.right_shift + comparison_obj.gapped_parse.gapped_bar_num - 1
		else:
			self.replacing_arr_index = comparison_obj.gapped_parse.gapped_bar_num + comparison_obj.right_shift - 1
		temp_extended_copy = copy.deepcopy(comparison_obj.comparison_extended_piece)
		temp_replaced_bar = temp_extended_copy.pop(self.replacing_arr_index)
		self.get_edit_distance(comparison_obj.gapped_extended_piece, temp_extended_copy)
		if temp_replaced_bar != '    ':
			self.actual_replaced_bar_num = self._get_replaced_bar_num()
			self.replaced_bar = temp_replaced_bar

	def _get_replaced_bar_num(self):
		number = self.replacing_arr_index - self.comparison_obj.left_shift + 1
		return number

	def get_edit_distance(self, gapped, temp_comparison):	
		trimmed = self._trim(gapped, temp_comparison)
		gapped = trimmed[0]
		temp_comparison = trimmed[1]
		n = len(gapped)
		m = len(temp_comparison)

		distance = [[0 for i in range(m+1)] for j in range(n+1)]

		for i in range(1,n+1):
			distance[i][0] = distance[i-1][0] + self._insert_cost(gapped[i-1])

		for j in range(1,m+1):
			distance[0][j] = distance[0][j-1] + self._delete_cost(temp_comparison[j-1])

		for i in range(1,n+1):
			for j in range(1,m+1):
				distance[i][j] = min(distance[i-1][j] + 1,
				distance[i][j-1] + 1,
				distance[i-1][j-1] + self._subst_cost(temp_comparison[j-1],gapped[i-1]))

		self.edit_distance = distance[n][m]

	def _trim(self, x, y):
		first_x = -1
		first_y = -1
		last_x = -1
		last_y = -1
		first_hit_x = False
		first_hit_y = False

		for i in range(len(x)):
			if first_hit_x == False and x[i] != '   ':
				first_hit_x = True
				first_x = i
			if first_hit_x == True and x[i] == '    ':
				last_x = i
				break

		for j in range(len(y)):
			if first_hit_y == False and y[j] != '    ':
				first_hit_y = True
				first_y = j
			if first_hit_y == True and y[j] == '    ':
				last_y = j
				break

		if first_x == -1:
			first_x = 0
		if first_y == -1:
			first_y = 0
		if last_x == -1:
			last_x = len(x)
		if last_y == -1:
			last_y = len(y)

		first = min(first_x, first_y)
		last = max(last_x, last_y)
		return(x[first:last], y[first:last])

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

	def  fill_database(self):
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
	
	# ground_truth_x = musicXML_parsing.MusicXMLParsing('../musicXML/palestrina/Missa-Petra-sancta_Benedictus_Palestrina-Giovanni-Pierluigi-da_file1.krn')

	
	# database = []

	database = Corpus("path-list.txt", "parsable-path-list.txt")
	database.fill_database()

	# ground_truth_x.create_gap(3)

	# align = SimpleAlignment(pitch_x, pitch_y, 'rhythm')
	# print 'edit distance: ', align.min_edit_obj.edit_distance
	# print 'replaced bar: ', align.min_edit_obj.replaced_bar
	# print 'replaced bar number: ', align.min_edit_obj.actual_replaced_bar_num

main()
