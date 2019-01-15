import pandas as pd


class GeneHandler:
    def __init__(self, gene_reference_path, header=None):
        self.gene_reference_path = gene_reference_path
        if header is None:
            header = [
                "geneName",
                "name",
                "chrom",
                "strand",
                "txStart",
                "txEnd",
                "cdsStart",
                "cdsEnd",
                "exonCount",
                "exonStarts",
                "exonEnds",
            ]
        self._refFlat = pd.read_csv(
            gene_reference_path, sep="\t", low_memory=False, names=header
        ).fillna("N/A")

    def find_nearest_gene(
        self, chromosome: str, insertion_site: int
    ) -> (str, str):
        found = False
        gene = ""
        color_grad = [
            "rgb(180, 218, 4)",
            "rgb(60, 211, 4)",
            "rgb(4, 204, 59)",
            "rgb(4, 197, 163)",
            "rgb(3, 119, 190)",
        ]
        a = self._refFlat.query(
            'chrom == "'
            + chromosome
            + '" and txStart < '
            + str(insertion_site)
            + " and "
            + str(insertion_site)
            + " < txEnd"
        )
        color = ""
        for each in a.itertuples():
            in_exon = False
            gene = ""
            color = ""
            for x in range(each.exonCount):
                if (
                    int(each.exonStarts.split(",")[x])
                    < insertion_site
                    < int(each.exonEnds.split(",")[x])
                ):
                    gene = each.geneName
                    color = "red"
                    in_exon = True
            if not in_exon:
                gene = each.geneName
                color = "orange"
            found = True
        if not found:
            input_chromosome = insertion_site
            subs = self._refFlat.query('chrom == "' + chromosome + '"')
            subs = subs.reset_index()
            closest_start = next(
                subs.ix[
                    (subs["txStart"] - input_chromosome).abs().argsort()[:1]
                ].itertuples()
            )
            closest_end = next(
                subs.ix[
                    (subs["txEnd"] - input_chromosome).abs().argsort()[:1]
                ].itertuples()
            )

            if closest_start.Index == closest_end.Index:
                dist = abs(closest_start.txStart - input_chromosome)
                gene = closest_start.geneName
            else:
                closest = (
                    closest_start
                    if abs(closest_start.txStart - input_chromosome)
                    < abs(closest_end.txEnd - input_chromosome)
                    else closest_end
                )
                dist = (
                    abs(closest.txStart - input_chromosome)
                    if abs(closest.txStart - input_chromosome)
                    < abs(closest.txEnd - input_chromosome)
                    else abs(closest.txEnd - input_chromosome)
                )
                gene = closest.geneName
            color = color_grad[4]
            if dist <= 300:
                color = color_grad[0]
            elif 300 < dist <= 1000:
                color = color_grad[1]
            elif 1000 < dist <= 3000:
                color = color_grad[2]
            elif 3000 < dist <= 10000:
                color = color_grad[3]
            elif 10000 < dist:
                color = color_grad[4]

        return gene, color
