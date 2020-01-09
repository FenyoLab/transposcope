import logging


class ReadsDict(dict):
    def __iadd__(self, other):
        self.update(other)
        return self

    def reads_from_key_list(self, readid_list):
        for key in readid_list:
            yield self[key]

    def insert(self, v):
        # 0x800 and 0x100 should be ignored
        # This should be logged
        if v.flag & (0x800 | 0x100):
            # logging.info("Supplementary read was discarded: %s", v.query_name)
            return False
        else:

            found_read = self[v.query_name]
            if len(found_read) == 2 and None not in found_read:
                return -1
            elif len(found_read) > 2:
                raise ValueError(
                    "There should not be more than two reads "
                    "with the same query name: ({})".format(v.query_name)
                )
            elif len(found_read) == 0:
                raise ValueError("There should not be empty lists at this point")
            else:
                self[v.query_name][v.is_read2] = v
            return True
