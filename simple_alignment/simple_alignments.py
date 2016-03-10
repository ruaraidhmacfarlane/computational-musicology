import copy, musicXML_parsing


class SimpleAlignment:

	gapped_piece = None
	comparison_piece = None
	gapped_extended_piece = []
	comparison_extended_piece = []
	extended_length = 0
	min_edit_alignments = []

	def __init__(self, gapped, comparison):
		self.gapped_piece = gapped
		self.comparison_piece = comparison
		self.extended_length = gapped.length + comparison.length
		self.align()

	def align(self):
		self.extend()
		print self.gapped_extended_piece
		print self.comparison_extended_piece

		for i in range(self.extended_length):
			self.adjust(i)
			# self.min_edit_alignments.append(EditDistance(i, self))

	def extend(self):
		a = ['    '] * self.gapped_piece.length
		b = ['    '] * self.comparison_piece.length
		self.gapped_extended_piece = copy.deepcopy(self.gapped_piece).rhythm_hash + a
		self.comparison_extended_piece = b + copy.deepcopy(self.comparison_piece).rhythm_hash

	def adjust(self, adjust_index):
		if adjust_index % 2 == 0:
			swap = self.gapped_extended_piece.pop()
			self.gapped_extended_piece = [swap] + self.gapped_extended_piece
		else:
			swap = self.comparison_extended_piece.pop(0)
			self.comparison_extended_piece = self.comparison_extended_piece + [swap]

		print self.gapped_extended_piece
		print self.comparison_extended_piece



class EditDistance:

	edit_distance = -1
	replaced_bar = None
	replaced_bar_num = 0
	adjust_index = -1
	comparison_obj = None

	def __init__(self, index, comparison_obj):
		self.adjust_index = index
		self.comparison_obj = comparison_obj
		self.adjust()
		# self.min_edit_distance()
		

	# def edit_distance():	
	# 	# x and y do they have gaps?
	# 	n = len(x)
	#     m = len(y)
	    
	#     distance = [[0 for i in range(m+1)] for j in range(n+1)]

	#     for i in range(1,n+1):
	#         distance[i][0] = distance[i-1][0] + insertCost(x[i-1])

	#     for j in range(1,m+1):
	#         distance[0][j] = distance[0][j-1] + deleteCost(y[j-1])

	#     for i in range(1,n+1):
	#         for j in range(1,m+1):
	#             distance[i][j] = min(distance[i-1][j] + 1,
	#                                  distance[i][j-1] + 1,
	#                                  distance[i-1][j-1] + substCost(y[j-1],x[i-1]))

 #    	self.edit_distance = distance[n][m]

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