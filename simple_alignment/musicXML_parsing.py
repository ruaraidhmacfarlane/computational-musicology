import music21, sys, copy


class MusicXMLParsing:

	parsed_score = None
	rhythm_hash = []
	parsons_hash = []
	length = 0
	gapped_bar_num = 0
	# Hard coded for now until gaps in bars get bigger
	GAP_LENGTH = 1

	def __init__(self, path):
		self.parsed_score = music21.converter.parse(path)
		self.rhythm_hash = music21.omr.correctors.ScoreCorrector(self.parsed_score).singleParts[0].hashedNotes
		self.length = len(self.rhythm_hash)
		self.parsons_hash = self._parsons_code()

	def create_gap(self, bar):
		if bar <= len(self.rhythm_hash):
			# self.gapped_score_rhythm = copy.deepcopy(self.rhythm_hash)
			# self.gapped_score_rhythm.pop(bar-1)
			# self.gapped_score_rhythm.append('    ')
			self.gapped_bar_num = bar
		else:
			sys.exit("Error: Cannot create a gap, bar is out of range of music")

	"""
	u = "up," if the note is higher than the previous note
	d = "down," if the note is lower than the previous note
	r = "repeat," if the note is the same pitch as the previous note
	* = first tone as reference
	"""
	def _parsons_code(self):
		contour_arr = []
		for pitch in self.parsed_score.pitches:
			if len(contour_arr) == 0:
				last_pitch = pitch.nameWithOctave
				contour_arr.append('*')
			else:
				if pitch.nameWithOctave < last_pitch:
					contour_arr.append('d')
				elif pitch.nameWithOctave > last_pitch:
					contour_arr.append('u')
				else:
					contour_arr.append('r')
				last_pitch = pitch.nameWithOctave
		return contour_arr
