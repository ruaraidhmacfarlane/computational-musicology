import music21, sys


class MusicXMLParsing:

	parsed_score = None
	rhythm_hash = []
	parsons_hash = []
	gapped_score_rhythm = []
	length = 0
	gapped_bar_num = 0

	def __init__(self, path):
		self.parsed_score = music21.converter.parse(path)
		self.rhythm_hash = music21.omr.correctors.ScoreCorrector(self.parsed_score).singleParts[0].hashedNotes
		self.length = len(self.rhythm_hash)
	# def parsons_code(self):		

	# Only to work for hashed rhythms for now, when parsons is included this will create a gap in that array too
	def create_gap(self, bar):
		if bar <= len(self.rhythm_hash):
			self.gapped_score_rhythm = self.rhythm_hash
			self.gapped_score_rhythm.pop(bar-1)
			# self.gapped_score_rhythm.append('    ')
			self.gapped_bar_num = bar
		else:
			sys.exit("Error: Cannot create a gap, bar is out of range of music")



