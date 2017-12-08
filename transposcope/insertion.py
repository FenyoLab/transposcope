class Insertion:
    def __init__(self, chromosome=None, target_start=None, target_end=None, clip_start=None,
                 clip_end=None, pred=None, clip_sc=None, line1_end=None,named_tuple=None):
        self.COMPLEMENT = False
        self.GENOME_SEQUENCE = None
        self.LINE1_SEQUENCE = None
        if named_tuple:
            self.CLIP_START = named_tuple.H2_ClipS
            self.CLIP_END = named_tuple.H3_ClipE
            self.PRED = named_tuple.H31_pred
            self.CHROMOSOME = named_tuple.H1_ClipChr
            self.TARGET_START = named_tuple.H6_TargS
            self.TARGET_END = named_tuple.H7_TargE
            self.CLIP_SC = named_tuple.H4_ClipSC
            self.ALL_COLUMNS = named_tuple
        else:
            self.CLIP_START = clip_start
            self.CLIP_END = clip_end
            self.PRED = pred
            self.CHROMOSOME = chromosome
            self.TARGET_START = target_start
            self.TARGET_END = target_end
            self.CLIP_SC = 0
            self.ALL_COLUMNS = {'a': self.CLIP_START,
                                'b': self.CLIP_END,
                                'c': self.PRED,
                                'd': self.TARGET_START,
                                'e': self.TARGET_END,
                                'f': self.CLIP_SC}
        self.keys_of_reads_in_target_region = None
        self.calculate_if_insertion_is_complement()
        if self.COMPLEMENT:
            # TS                             CS    CE/TE
            # |------------------------------|------|TTTTT LINE1
            self.START = self.TARGET_START - 1
            # self.END = max(self.CLIP_END, self.TARGET_END)
            self.END = self.CLIP_END - 1
            self.INSERTION_SITE = self.CLIP_END
        else:
            #            CS/TS    CE                          TE
            # LINE1 AAAAA  |------|---------------------------|
            # self.START = min(self.CLIP_START, self.TARGET_START)
            self.START = self.CLIP_START - 1
            self.END = self.TARGET_END
            self.INSERTION_SITE = self.CLIP_START

    def calculate_if_insertion_is_complement(self):
        if (self.CLIP_START + self.CLIP_END) / 2 > (self.TARGET_START + self.TARGET_END) / 2:
            self.COMPLEMENT = True

    def set_reads_found_in_target_region(self, reads):
        """

        :param reads: 
        """
        self.reads_in_target_region = reads

    def __str__(self) -> str:
        return self.CHROMOSOME + ':' + str(self.TARGET_START) + '-' + str(self.TARGET_END)

    def __repr__(self) -> str:
        return self.CHROMOSOME + ':' + str(self.TARGET_START) + '-' + str(
            self.TARGET_END) + '(' + str(len(self.reads_in_target_region)) + ')'


