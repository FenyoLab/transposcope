class Insertion:
    def __init__(self, named_tuple):
        # TODO - Make sure that these variables are needed
        self.five_prime_sequence = ""
        self.three_prime_sequence = ""
        self.me_sequence = ""

        self.chromosome = named_tuple.chromosome
        self.five_prime_target = named_tuple.target_5p
        self.three_prime_target = named_tuple.target_3p
        self.insertion_window = named_tuple.window
        self.strand = named_tuple.me_strand
        self.all_info = named_tuple._asdict()
        self.me_start = named_tuple.me_start - 1
        self.me_end = named_tuple.me_end

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
