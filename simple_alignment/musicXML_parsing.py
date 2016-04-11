import music21
import sys


class MusicXMLParsing:
    name = ""
    parsed_score = None
    rhythm_hash = []
    # pitch_hash = []
    parsons_code = []
    length = 0
    previous_parsons_bar = ""
    previous_rhythm_bar = ""
    gapped_bar_num = 0
    # Hard coded for now until gaps in bars get bigger
    GAP_LENGTH = 1

    def __init__(self, path):
        self.name = self._get_filename(path)
        if (self.is_kern(path)):
            path = music21.converter.parse(path).write('musicxml')
        if (self.is_midi(path)):
            path = music21.converter.parse(path).write('musicxml')
        self.parsed_score = music21.converter.parse(path)
        # self.parsed_score.show()
        # self.parsed_work = music21.parseWork(path)
        self.rhythm_hash = music21.omr.correctors.ScoreCorrector(self.parsed_score).singleParts[0].hashedNotes
        self.length = len(self.rhythm_hash)
        # self.pitch_hash = self._hash_pitches()
        self.parsons_code = self._parsons_code()
        # print self.rhythm_hash
        # print self.parsons_code

        self.parsed_score = None

    @staticmethod
    def is_kern(path_name):
        split_path = path_name.split('.')
        if split_path[-1] == 'krn':
            return True
        else:
            return False

    @staticmethod
    def is_midi(path_name):
        split_path = path_name.split('.')
        if split_path[-1] == 'mid':
            return True
        else:
            return False


    def create_gap(self, bar):
        if bar <= len(self.rhythm_hash):
            self.gapped_bar_num = bar
            self.previous_rhythm_bar = self.rhythm_hash[bar - 1]
            self.previous_parsons_bar = self.parsons_code[bar - 1]
            self.rhythm_hash[bar - 1] = ''
            self.parsons_code[bar - 1] = ''
        else:
            sys.exit("Error: Cannot create a gap, bar is out of range of music")

    def fill_gap(self, bar_num, bar, mode):
        if mode == "rhythm":
            self.rhythm_hash[bar_num - 1] = bar
        elif mode == "parson":
            self.parsons_code[bar_num - 1] = bar
    """
	u = "up," if the note is higher than the previous note
	d = "down," if the note is lower than the previous note
	r = "repeat," if the note is the same pitch as the previous note
	* = first tone as reference
	"""

    def _parsons_code(self):
        print "Im parson code function fix me"
        contour_arr = []
        measure_map = self.parsed_score.parts[0].measureOffsetMap()
        measures = sorted(measure_map)
        for m in measures:
            bar_string = ""
            # maybe first bars are rests
            if len(measure_map[m][0].notes.pitches) != 0:
                index = len(contour_arr)
                for pitch in measure_map[m][0].notes.pitches:
                    if index == 0 and len(bar_string) == 0:
                        last_pitch = pitch
                        bar_string += '*'
                    else:
                        bar_string += self._compare_pitch(last_pitch, pitch)
                        last_pitch = pitch
                contour_arr.append(bar_string)
        return contour_arr

    def _compare_pitch(self, last_pitch, pitch):
        pitch_list = ['C', 'C#', 'D-', 'D', 'D#', 'E-', 'E', 'F-', 'E#', 'F', 'F#', 'G-', 'G', 'G#', 'A-', 'A', 'A#',
                      'B-', 'B', 'C-', 'B#']
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

                # def _convert_bars(self, contour_arr):

    @staticmethod
    def _get_filename(path):
        split_name = path.split('/')
        directory_len = len(split_name)
        filename = split_name[directory_len - 1].split('.')
        name = filename[0]
        return name
