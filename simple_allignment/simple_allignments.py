import copy, musicXML_parsing


# class will be easier to work with
class SimpleAllignment:

	gapped_piece = []
	comparison_piece = []

# this could be a constructor
def simple_allignment(gapped_piece, comparison_piece):
	extended_length = len(extended_pieces[0])

	for bar in range(extended_length):
		fill_arr(i, gapped_piece.rhythm_hash, comparison_piece.rhythm_hash)

# def simple_allignment(gapped_piece, comparison_piece):
# 	comparison_arr_size = gapped_piece.length + comparison_piece.length
# 	# Just using it for rhythms so far
# 	extended_pieces = extend(gapped_piece.gapped_score_rhythm, comparison_piece.rhythm_hash)
# 	gapped_piece_extended = extended_pieces[0]
# 	comparison_piece_extended = extended_pieces[1]

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

# def find_gap_bar(replacing_bars, edit_distances):
# 	return replacing_bars[edit_distances.index(min(edit_distances))]

def extend(x, y):
	a = ['    '] * len(y)
	b = ['    '] * len(x)
	x_extended = x + a
	y_extended = b + y
	return(x_extended, y_extended)

def fill_arr(index, x, y):
	extended_pieces = extend(x, y)
	if index % 2 == 0:
		swap = extended_pieces[0].pop()
		extended_pieces[0] = [swap] + extended_pieces[0]
	else:
		swap = extended_pieces[1].pop(0)
		extended_pieces[1] = extended_pieces[1] + [swap]

	return (extended_pieces[0], extended_pieces[1])

def substCost(x, y):
    if x == y: 
        return 0
    else: 
        return 2
    
def insertCost(x):
    return 1

def deleteCost(x):
    return 1

def edit_distance(x, y):
    n = len(x)
    m = len(y)
    
    distance = [[0 for i in range(m+1)] for j in range(n+1)]

    for i in range(1,n+1):
        distance[i][0] = distance[i-1][0] + insertCost(x[i-1])

    for j in range(1,m+1):
        distance[0][j] = distance[0][j-1] + deleteCost(y[j-1])

    for i in range(1,n+1):
        for j in range(1,m+1):
            distance[i][j] = min(distance[i-1][j] + 1,
                                 distance[i][j-1] + 1,
                                 distance[i-1][j-1] + substCost(y[j-1],x[i-1]))
    return distance[n][m]

def main():
	a = musicXML_parsing.MusicXMLParsing('../musicXML/tests/rhythm-test.xml')
	b = musicXML_parsing.MusicXMLParsing('../musicXML/tests/rhythm-test.xml')

	a.create_gap(3)

	replaced_bar = simple_allignment(a, b)
	# print replaced_bar
	return

main()