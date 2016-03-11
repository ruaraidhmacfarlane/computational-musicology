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
			print pitch.nameWithOctave
			if len(contour_arr) == 0:
				last_pitch = pitch
				contour_arr.append('*')
			else:
				contour_arr.append(self._compare_pitch(last_pitch, pitch))
				last_pitch = pitch
		return contour_arr

	def _compare_pitch(self, last_pitch, pitch):
		pitch_list = ['C', 'C#', 'D-', 'D', 'D#', 'E-', 'E', 'F-', 'E#' , 'F', 'F#', 'G-', 'G', 'G#', 'A-', 'A', 'A#', 'B-', 'B', 'C-', 'B#']
		if last_pitch.nameWithOctave == pitch.nameWithOctave:
			return 'r'
		if last_pitch.octave != pitch.octave:
			if last_pitch.octave < pitch.octave:
				return 'u'
			else:
				return 'd'
		else:
			last_pitch_index = pitch_list.index(last_pitch.name)
			curr_pitch_index = pitch_list.index(pitch.name)
			if last_pitch_index < curr_pitch_index:
				return 'u'
			else:
				return 'd'
