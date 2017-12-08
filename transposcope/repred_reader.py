from collections import namedtuple


class RepredReader:
    def __init__(self, repred_file_path, repred_type='tipseq', header=None):
        """

        :param repred_file_path: 
        :param repred_type: 
        :param header: 
        """
        self.repred_type = repred_type
        if header is None:
            header = {
                'strings': ['H1_ClipChr'],
                'ints': ['H2_ClipS', 'H3_ClipE', 'H4_ClipSC', 'H6_TargS', 'H7_TargE'],
                'floats': ['H30_label', 'H31_pred']
            }
        try:
            self.repred_file = open(repred_file_path, 'r')
        except IOError:
            print('repred file path invalid')
        self.header = header
        self.all_headers = self.repred_file.readline().strip().split('\t')
        # TODO - only save the columns that matter
        self.RepredLine = namedtuple('RepredLine', self.all_headers)

    def __parse_line(self, line):
        line = line.strip().split('\t')
        # TODO check if this should be a dict
        line = dict(zip(self.all_headers, line))
        needed_values_from_file = line
        for string in self.header['strings']:
            needed_values_from_file[string] = line[string]
        for integer in self.header['ints']:
            needed_values_from_file[integer] = int(line[integer])
        for floating_point in self.header['floats']:
            needed_values_from_file[floating_point] = float(line[floating_point])
        return needed_values_from_file

    def read_lines(self):
        """
        Iterator which returns the next line of the file as a named tuple

        :rtype: named_tuple(H1_ClipChr, H2_ClipS, H3_ClipE, H6_TargS, H7_TargE, H31_pred)
        """
        for line in self.repred_file.readlines():
            line = self.__parse_line(line)
            line_with_header = self.RepredLine(**line)
            yield (line_with_header)
