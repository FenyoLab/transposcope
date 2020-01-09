import json


class Insertion:
    """A class which holds the coordinates and meta data for each insertion

    :param insertion_data: A preformated named tuple containing information regarding an insertion
    :type named tuple
    
    """

    def __init__(self, insertion_data):
        self.five_prime_sequence = ""
        self.three_prime_sequence = ""
        self.me_sequence = ""

        self.longest_read = None

        self.chromosome = insertion_data.chromosome
        self.five_prime_target = insertion_data.target_5p  # start and end coordinate
        self.three_prime_target = insertion_data.target_3p
        self.insertion_window = insertion_data.window
        self.strand = insertion_data.me_strand
        self.all_info = insertion_data._asdict()
        self.me_start = insertion_data.me_start
        self.me_end = insertion_data.me_end
        self.type = insertion_data.type
        self.pred = insertion_data.pred

        self.read_keys_in_target_region = None

        self.insertion_site = (
            self.five_prime_target[1]
            if self.five_prime_target
            else self.three_prime_target[0]
        )

    def set_reads_found_in_target_region(self, reads):
        self.reads_in_target_region = reads

    def __str__(self):
        return "{}:{}|{} {}".format(
            self.chromosome,
            self.five_prime_target,
            self.three_prime_target,
            len(self.read_keys_in_target_region),
        )

    def __repr__(self):
        return (
            self.chromosome
            + ":"
            + str(self.five_prime_target)
            + "-"
            + str(self.three_prime_target)
            + "("
            + str(len(self.reads_in_target_region))
            + ")"
        )
