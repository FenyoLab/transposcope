import logging


class ReadsDict(dict):
    def __iadd__(self, other):
        self.update(other)
        return self

    def reads_from_key_list(self, readid_list):
        for key in readid_list:
            yield self[key]

    def insert(self, v):
        # TODO: Only add primary alignments
        # 0x800 and 0x100 should be ignored
        # This should be logged
        if v.flag & (0x800 | 0x100):
            # TODO: Add documentation indicating that these reads are discarded
            # logging.info('Non primary or secondary alignment discarded {}'.format(v.query_name))
            return False
        else:
            found_read = self[v.query_name]
            if len(found_read) == 2:
                return -1
            elif len(found_read) > 2:
                raise ValueError(
                    "There should not be more than two reads "
                    "with the same query name: ({})".format(v.query_name)
                )
            elif len(found_read) == 0:
                raise ValueError("There should not be empty lists at this point")
            else:
                if (
                    found_read[0].is_read2
                    and v.is_read1
                    or found_read[0].is_read1
                    and v.is_read2
                ):
                    self[v.query_name].insert(v.is_read2, v)
                    return 0
            return True
