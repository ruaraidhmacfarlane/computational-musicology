import copy, musicXML_parsing


class SimpleAlignment:

	gapped_parse = None
	comparison_parse = None
	gapped_extended_piece = []
	comparison_extended_piece = []
	extended_length = 0
	min_edit_alignments = []
	gapped_piece_shift = 0

	def __init__(self, gapped, comparison):
		self.gapped_parse = gapped
		self.comparison_parse = comparison
		self.extended_length = gapped.length + comparison.length
		self.align()

	def align(self):
		self.extend()
		self.create_gap()

		# its -1 because gaps were created... maybe in create gaps length should be decremented
		for i in range(self.extended_length):
			self.min_edit_alignments.append(EditDistance(i, self))
			self.adjust(i)
		print self.gapped_extended_piece
		print self.comparison_extended_piece	

	def extend(self):
		a = ['    '] * self.gapped_parse.length
		# its -1 because gaps were created
		b = ['    '] * self.comparison_parse.length
		self.gapped_extended_piece = copy.deepcopy(self.gapped_parse).rhythm_hash + a
		self.comparison_extended_piece = b + copy.deepcopy(self.comparison_parse).rhythm_hash

	def create_gap(self):
		self.gapped_extended_piece.pop(self.gapped_parse.gapped_bar_num - 1)
		self.gapped_extended_piece.append('    ')
		# self.comparison_extended_piece.pop(0)

	def adjust(self, adjust_index):
		if adjust_index % 2 == 0:
			swap = self.gapped_extended_piece.pop()
			self.gapped_extended_piece = [swap] + self.gapped_extended_piece
			self.gapped_piece_shift += 1
		else:
			swap = self.comparison_extended_piece.pop(0)
			self.comparison_extended_piece = self.comparison_extended_piece + [swap]

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
		# print comparison_obj.gapped_extended_piece
		# print comparison_obj.comparison_extended_piece
		if self.adjust_index % 2 == 0:
			self.replacing_arr_index = comparison_obj.gapped_piece_shift + comparison_obj.gapped_parse.gapped_bar_num - 1
		else:
			self.replacing_arr_index = comparison_obj.gapped_parse.gapped_bar_num + comparison_obj.gapped_piece_shift - 1
		print self.replacing_arr_index
		temp_extended_copy = copy.deepcopy(comparison_obj.comparison_extended_piece)
		temp_replaced_bar = temp_extended_copy.pop(self.replacing_arr_index)
		self.get_edit_distance(comparison_obj.gapped_extended_piece, temp_extended_copy)
		if temp_replaced_bar != '    ':
			self.replaced_bar = temp_replaced_bar
			print self.replaced_bar
		

		# self.create_gaps()
		# self.min_edit_distance()

		# comparison_bar_index = self.comparison_obj.gapped_extended_piece.length - self.adjust_index
		# self.comparison_obj.comparison_extended_piece.pop(self.comparison_obj.gapped_bar_num + self.adjust_index)

	def get_edit_distance(self, gapped, temp_comparison):	
		# x and y do they have gaps?

		print gapped
		print temp_comparison

		n = len(gapped)
		m = len(temp_comparison)
	    
	  #   distance = [[0 for i in range(m+1)] for j in range(n+1)]

	  #   for i in range(1,n+1):
	  #       distance[i][0] = distance[i-1][0] + insertCost(x[i-1])

	  #   for j in range(1,m+1):
	  #       distance[0][j] = distance[0][j-1] + deleteCost(y[j-1])

	  #   for i in range(1,n+1):
	  #       for j in range(1,m+1):
	  #           distance[i][j] = min(distance[i-1][j] + 1,
	  #                                distance[i][j-1] + 1,
	  #                                distance[i-1][j-1] + substCost(y[j-1],x[i-1]))

	 	# self.edit_distance = distance[n][m]

	def _subst_cost(x, y):
	    if x == y: 
	        return 0
	    else: 
	        return 2

	def _insert_cost(x):
	    return 1

	def _delete_cost(x):
	    return 1


# def simple_allignment(gapped_piece, comparison_piece):

# 	gapped_piece_index = 0
# 	replacing_bar_arr = []
# 	min_edits_arr = []

# 	for i in range(comparison_arr_size):
# 		tuple_arr = fill_arr(i, gapped_piece_extended, comparison_piece_extended)
# 		gapped_piece_extended = tuple_arr[0]
# 		comparison_piece_extended = tuple_arr[1]

# 		temp_gapped_piece_extended = copy.deepcopy(gapped_piece_extended)
# 		temp_comparison_piece_extended = copy.deepcopy(comparison_piece_extended)

# 		print temp_gapped_piece_extended
# 		print temp_comparison_piece_extended

		# if i % 2 == 1:
		# 	gapped_piece_index += 1

		# bar_num = gapped_piece_index + gapped_piece.gapped_bar_num - 1
		# removed_bar = temp_gapped_piece_extended.pop(bar_num)
		# replacing_bar_arr.append(temp_comparison_piece_extended.pop(bar_num))

	# 	min_edits_arr.append(edit_distance(temp_gapped_piece_extended, temp_comparison_piece_extended))

	# returned_bar = find_gap_bar(replacing_bar_arr, min_edits_arr)
	# min_edit_distance = min(min_edits_arr)

	# return returned_bar, min_edit_distance

def fill_arr(index, x, y):
	extended_pieces = extend(x, y)
	if index % 2 == 0:
		swap = extended_pieces[0].pop()
		extended_pieces[0] = [swap] + extended_pieces[0]
	else:
		swap = extended_pieces[1].pop(0)
		extended_pieces[1] = extended_pieces[1] + [swap]

	return (extended_pieces[0], extended_pieces[1])
    
def main():
	a = musicXML_parsing.MusicXMLParsing('../musicXML/tests/rhythm-test.xml')
	b = musicXML_parsing.MusicXMLParsing('../musicXML/tests/rhythm-test.xml')

	a.create_gap(3)

	align = SimpleAlignment(a, b)


	# replaced_bar = simple_allignment(a, b)
	# print replaced_bar
	return

main()