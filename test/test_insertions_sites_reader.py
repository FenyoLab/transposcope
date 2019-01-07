from unittest import TestCase
from unittest import mock

from src.transposcope.insertion_sites_reader import InsertionSiteReader


class TestRepredReader(TestCase):
    @mock.patch("builtins.open",
                mock.mock_open(read_data="""H1_ClipChr	H2_ClipS	H3_ClipE	H4_ClipSC	H5_TargChr	H6_TargS	H7_TargE	H8_TargRDs	H9_TargBPs	H10_TargMis	H11_TargInd	H12_TargClip	H13_ConSen	H14_PolyA	H15_PolyT	H16_PolyAT	H17_IfGS	H18_EnzmCS	H19_EnzmCnt	H20_TargUniq	H21_TargProp	H22_L1HsPrim	H23_W	H24_D	H25_VaritIdx	H26_PolyAT	H27_SC	H28_Uniq	H29_Prop	H30_label	H31_pred
chr1	105386450	105386456	312	chr1	105383518	105386455	6226	569194	2523	155	1787	TTTTTTTTTTT	0	1	1	chr1-105386455-105392486	AseI-258:BspHI-1571:BstYI-2566	258-1597.1976744186047:1571-108.2564687975647:2566-14.52008032128514	4984	1373	a(5904)	11.5206186805563	7.5453196334392	0.465399186681033	1	8.28540221886225	80.051397365885	27.5481540930979	1	1"""))
    def test_get_next(self):
        parser = InsertionSiteReader('test.txt')
        updater = parser.read_lines()
        update = next(updater)
        self.assertEqual("chr1", update.H1_ClipChr)
        self.assertEqual(105386450, update.H2_ClipS)
        self.assertEqual(105386456, update.H3_ClipE)
        self.assertEqual(105383518, update.H6_TargS)
        self.assertEqual(105386455, update.H7_TargE)
        self.assertEqual(1, update.H31_pred)
