# # pylint: disable=redefined-outer-name
# """
# File: test_melt_parser.py
# Author: Mark Grivainis
# Email: mark.grivainis@fenyolab.org
# Github: https://github.com/FenyoLab/transposcope
# Description: Test case definitions for a MELT vcf parser
# """
#
# import pytest
#
# from src.transposcope.parsers import melt_parser
#
#
# @pytest.fixture()
# def melt_file_handler():
#     """Fixture definition which loads the test file
#        for test cases
#
#     @return:  file reader object
#     @rtype :  Generator
#     """
#     return melt_parser.load_vcf("test/parsers/examples/melt.vcf")
#
#
# def test_meta_info_extraction(melt_file_handler):
#     """Test case which determines whether meta data is correctly
#     parsed from the example file
#
#     @param param:  melt_file_handler
#     @type  param:  Generator
#
#     """
#
#     meta_data, _ = melt_parser.parse_meta_info(melt_file_handler)
#     assert meta_data["fileformat"] == "VCFv4.2"
#     assert meta_data["source"] == "MELTv2.1.5"
#     assert meta_data["reference"] == "hg38.fa"
#     assert (
#         meta_data["ALT"]["INS:ME:LINE1"]["Description"]
#     ) == "Insertion of LINE1 element"
#     assert meta_data["contig"]["chr1"]["length"] == "248956422"
#     assert meta_data["contig"]["chr2"]["length"] == "242193529"
#     assert meta_data["contig"]["chr3"]["length"] == "198295559"
#     assert meta_data["contig"]["chr4"]["length"] == "190214555"
#     assert meta_data["contig"]["chr5"]["length"] == "181538259"
#     assert meta_data["contig"]["chr6"]["length"] == "170805979"
#     assert meta_data["contig"]["chr7"]["length"] == "159345973"
#     assert meta_data["contig"]["chr8"]["length"] == "145138636"
#     assert meta_data["contig"]["chr9"]["length"] == "138394717"
#     assert meta_data["contig"]["chr10"]["length"] == "133797422"
#     assert meta_data["contig"]["chr11"]["length"] == "135086622"
#     assert meta_data["contig"]["chr12"]["length"] == "133275309"
#     assert meta_data["contig"]["chr13"]["length"] == "114364328"
#     assert meta_data["contig"]["chr14"]["length"] == "107043718"
#     assert meta_data["contig"]["chr15"]["length"] == "101991189"
#     assert meta_data["contig"]["chr16"]["length"] == "90338345"
#     assert meta_data["contig"]["chr17"]["length"] == "83257441"
#     assert meta_data["contig"]["chr18"]["length"] == "80373285"
#     assert meta_data["contig"]["chr19"]["length"] == "58617616"
#     assert meta_data["contig"]["chr20"]["length"] == "64444167"
#     assert meta_data["contig"]["chr21"]["length"] == "46709983"
#     assert meta_data["contig"]["chr22"]["length"] == "50818468"
#     assert meta_data["contig"]["chrX"]["length"] == "156040895"
#     assert meta_data["INFO"]["ASSESS"] == {
#         "Number": "1",
#         "Type": "Integer",
#         "Description": "Provides information on evidence availible to decide "
#         "insertion site.0 = No overlapping reads at site;"
#         "1 = Imprecise breakpoint due to greater than expected "
#         "distance between evidence;"
#         "2 = discordant pair evidence only -- No split read "
#         "information;"
#         "3 = left side TSD evidence only;"
#         "4 = right side TSD evidence only;"
#         "5 = TSD decided with split reads, "
#         "highest possible quality",
#     }
#     assert meta_data["INFO"]["TSD"] == {
#         "Number": "1",
#         "Type": "String",
#         "Description": "Precise Target Site Duplication for bases, if unknown,"
#         " value will be NULL",
#     }
#     assert meta_data["INFO"]["INTERNAL"] == {
#         "Number": "2",
#         "Type": "String",
#         "Description": "If insertion internal or close to a gene, listed here"
#         " followed by a discriptor of the location in the gene"
#         " (either INTRON, EXON_#, 5_UTR, 3_UTR, PROMOTER, or"
#         " TERMINATOR). If multiple genes intersected, will be"
#         " seperated by '\\|'",
#     }
#     assert meta_data["INFO"]["SVTYPE"] == {
#         "Number": "1",
#         "Type": "String",
#         "Description": "Type of structural variant",
#     }
#     assert meta_data["INFO"]["SVLEN"] == {
#         "Number": "1",
#         "Type": "Integer",
#         "Description": "Difference in length between REF and ALT alleles; "
#         "If unknown, will be -1",
#     }
#     assert meta_data["INFO"]["MEINFO"] == {
#         "Number": "4",
#         "Type": "String",
#         "Description": "Mobile element info of the form NAME,START,END,"
#         "POLARITY; If START or END is unknown, will be -1; "
#         "If POLARITY is unknown, will be 'null'",
#     }
#     assert meta_data["INFO"]["DIFF"] == {
#         "Number": ".",
#         "Type": "String",
#         "Description": "Coverage and Differences in relation to the LINE1 "
#         "reference. Form is %2XCoverage:Differences, "
#         "with differences delimited by ','",
#     }
#     assert meta_data["INFO"]["LP"] == {
#         "Number": "1",
#         "Type": "Integer",
#         "Description": "Total number of discordant pairs supporting the "
#         "left side of the breakpont",
#     }
#     assert meta_data["INFO"]["RP"] == {
#         "Number": "1",
#         "Type": "Integer",
#         "Description": "Total number of discordant pairs supporting the right"
#         " side of the breakpont",
#     }
#     assert meta_data["INFO"]["RA"] == {
#         "Number": "1",
#         "Type": "Float",
#         "Description": "Ratio between LP and RP, reported as log2(LP / RP)",
#     }
#     assert meta_data["INFO"]["PRIOR"] == {
#         "Number": "1",
#         "Type": "String",
#         "Description": "True if this site was not discovered in this dataset, "
#         "but was included on a provided priors list",
#     }
#     assert meta_data["INFO"]["SR"] == {
#         "Number": "1",
#         "Type": "Integer",
#         "Description": "Total number of SRs at the estimated breakpoint for "
#         "this site. Recomended to filter sites with <= 2 SRs",
#     }
#     assert meta_data["INFO"]["ISTP"] == {
#         "Number": "1",
#         "Type": "Integer",
#         "Description": "Will be approximate location of twin priming "
#         "breakpoint in relation to L1 reference; "
#         "0 if not twin primed; -1 if no measurement",
#     }
#     assert meta_data["FILTER"]["s25"] == {
#         "Description": "Greater than 25.0% of samples do not have data"
#     }
#     assert meta_data["FILTER"]["rSD"] == {
#         "Description": "Ratio of LP to RP is greater than 2.0 standard "
#         "deviations"
#     }
#     assert meta_data["FILTER"]["hDP"] == {
#         "Description": "More than the expected number of discordant pairs "
#         "at this site are also split"
#     }
#     assert meta_data["FILTER"]["ac0"] == {
#         "Description": "No individuals in this VCF file were identified with "
#         "this insertion"
#     }
#     assert meta_data["FILTER"]["lc"] == {
#         "Description": "MEI is embeded in a low complexity region"
#     }
#     assert meta_data["FORMAT"]["GT"] == {
#         "Number": "1",
#         "Type": "String",
#         "Description": "Genotype",
#     }
#     assert meta_data["FORMAT"]["GL"] == {
#         "Number": "3",
#         "Type": "Float",
#         "Description": "Genotype likelihood",
#     }
#
#
# def test_vcf_content_extraction(melt_file_handler):
#     """Test whether conent is correctly extracted from the example vcf file
#
#     @param param:  melt_file_handler
#     @type  param:  Generator
#     """
#
#     _, header = melt_parser.parse_meta_info(melt_file_handler)
#     insertions = melt_parser.parse_vcf_content(melt_file_handler, header)
#     line_1 = {
#         "CHROM": "chr1",
#         "POS": "100000",
#         "ID": ".",
#         "REF": "T",
#         "ALT": "<INS:ME:LINE1>",
#         "QUAL": ".",
#         "FILTER": "ac0",
#         "INFO": {
#             "TSD": "null",
#             "ASSESS": "2",
#             "INTERNAL": "NR_027055,PROMOTER",
#             "SVTYPE": "LINE1",
#             "SVLEN": "1939",
#             "MEINFO": "L1Ambig,0,6064,+",
#             "DIFF": "0.02:n1-4078,a4118g,c4125t,g4252a,g4267a,t4268c,"
#             "n4300-6019",
#             "LP": "1",
#             "RP": "6",
#             "RA": "-2.585",
#             "ISTP": "-1",
#             "PRIOR": "false",
#             "SR": "0",
#         },
#         "FORMAT": "GT:GL",
#         "SAMPLE_NAME": "0/0:-0.72,-50.57,-930.2",
#     }
#     line_2 = {
#         "CHROM": "chr2",
#         "POS": "200000",
#         "ID": ".",
#         "REF": "G",
#         "ALT": "<INS:ME:LINE1>",
#         "QUAL": ".",
#         "FILTER": "rSD;lc",
#         "INFO": {
#             "TSD": "null",
#             "ASSESS": "3",
#             "INTERNAL": "null,null",
#             "SVTYPE": "LINE1",
#             "SVLEN": "505",
#             "MEINFO": "L1Ambig,0,6064,+",
#             "DIFF": "0.07:n1-5512,t5535g,n5536,g5538c,n5552,n5562,n5564,"
#             "n5566,n5568,g5577a,c5590t,a5712g,d5743,n5745,a5821t,"
#             "c5836t,c5855t,c5878g,i5883t,g5883t,a5884g,c5899t,"
#             "c5928t,a5929g,c5930a,a5931g,a5989t,g6014a",
#             "LP": "1",
#             "RP": "38",
#             "RA": "-5.248",
#             "ISTP": "0",
#             "PRIOR": "false",
#             "SR": "19",
#         },
#         "FORMAT": "GT:GL",
#         "SAMPLE_NAME": "0/1:-535.8,-90.91,-1198.22",
#     }
#     assert insertions[0] == line_1
#     assert insertions[1] == line_2
#
#
# def test_table_generation(melt_file_handler):
#     """test for table generation method
#
#     @param melt_file_handler: melt file handler
#     @type  melt_file_handler: Generator
#
#     @return:  Description
#     @rtype :  Type
#
#     @raise e:  Description
#     """
#     # TODO - add more tests for negative strand cases was well as cases where
#     # strand may not be defined
#     row_0 = [
#         "chromosome",
#         "target_start",
#         "target_end",
#         "clip_start",
#         "clip_end",
#         "strand",
#         "pred",
#         "three_prime_end",
#         "enzyme_cut_sites",
#         "me_start",
#         "me_end"
#     ]
#     row_1 = ["chr1", 99000, 100000, 100000, 100000, "+", "L1Ambig",
#              False, "", 0, 6064]
#     row_2 = ["chr1", 100000, 101000, 100000, 100000, "+", "L1Ambig",
#              True, "", 0, 6064]
#     row_3 = ["chr2", 199000, 200000, 200000, 200000, "+", "L1Ambig",
#              False, "", 0, 6064]
#     row_4 = ["chr2", 200000, 201000, 200000, 200000, "+", "L1Ambig",
#              True, "", 0, 6064]
#
#     _, header = melt_parser.parse_meta_info(melt_file_handler)
#     insertions = melt_parser.parse_vcf_content(melt_file_handler, header)
#     required_data = melt_parser.retrieve_required_data(insertions)
#     assert required_data[0] == row_0
#     assert required_data[1] == row_1
#     assert required_data[2] == row_2
#     assert required_data[3] == row_3
#     assert required_data[4] == row_4
