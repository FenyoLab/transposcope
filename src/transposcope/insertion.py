class Insertion:
    def __init__(
        self,
        chromosome=None,
        target_start=None,
        target_end=None,
        clip_start=None,
        clip_end=None,
        pred=None,
        clip_sc=None,
        line1_end=None,
        named_tuple=None,
    ):
        # TODO - Make sure that these variables are needed
        self.ME_IS_COMPLEMENT = False
        self.GENOME_SEQUENCE = None
        self.LINE1_SEQUENCE = None
        if named_tuple:
            self.CLIP_START = named_tuple.clip_start
            self.CLIP_END = named_tuple.clip_end
            self.PRED = named_tuple.pred
            self.CHROMOSOME = named_tuple.chromosome
            self.TARGET_START = named_tuple.target_start
            self.TARGET_END = named_tuple.target_end
            self.STRAND = named_tuple.strand
            self.ALL_COLUMNS = named_tuple._asdict()
            self.LINE1_START = named_tuple.me_start - 1
            self.LINE1_END = named_tuple.me_end
            self.THREE_PRIME = named_tuple.three_prime_end
        self.read_keys_in_target_region = None
        # self.calculate_if_insertion_is_complement()
        self.ME_IS_COMPLEMENT = True if self.STRAND == '-' else False
        if (self.THREE_PRIME and self.ME_IS_COMPLEMENT) or (
                not self.THREE_PRIME and not self.ME_IS_COMPLEMENT):
            # TS                             CS    CE/TE
            # |------------------------------|------|TTTTT LINE1
            self.START = self.TARGET_START - 1
            # self.END = max(self.CLIP_END, self.TARGET_END)
            self.END = self.CLIP_END - 1
            self.INSERTION_SITE = self.CLIP_END
        else:
            #            CS/TS    CE                          TE
            # LINE1 AAAAA  |------|---------------------------|
            self.START = self.CLIP_START - 1
            # self.START = min(self.TARGET_START, self.CLIP_START) - 1
            self.END = self.TARGET_END
            self.INSERTION_SITE = self.CLIP_START

    def calculate_if_insertion_is_complement(self):
        if (self.CLIP_START + self.CLIP_END) / 2 > (
            self.TARGET_START + self.TARGET_END
        ) / 2:
            self.ME_IS_COMPLEMENT = True

    def set_reads_found_in_target_region(self, reads):
        self.reads_in_target_region = reads

    def __str__(self) -> str:
        return "{}:{}-{}".format(
            self.CHROMOSOME, self.TARGET_START, self.TARGET_END
        )

    def __repr__(self) -> str:
        return (
            self.CHROMOSOME
            + ":"
            + str(self.TARGET_START)
            + "-"
            + str(self.TARGET_END)
            + "("
            + str(len(self.reads_in_target_region))
            + ")"
        )
