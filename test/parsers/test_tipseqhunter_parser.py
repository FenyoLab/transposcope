import pytest

from src.transposcope.parsers import tipseqhunter_parser


@pytest.fixture()
def repred_dataframe():
    return tipseqhunter_parser.load_repred(
        'test/parsers/examples/tipseqhunter.repred'
    )


def test_load_repred(repred_dataframe):
    assert (10, 31) == repred_dataframe.shape


def test_repred_dataframe_validation(repred_dataframe):
    with pytest.raises(ValueError) as error:
        repred_dataframe.set_value(5, 'H1_ClipChr', 'chr##')
        repred_dataframe.set_value(1, 'H1_ClipChr', 'chr##')
        tipseqhunter_parser.validate_repred(repred_dataframe)
    assert 'In row(s) [3 7] the clipping chromosome ' + \
           'does not match the target chromosome.' in str(error.value)


def test_positive_strand_orientation_calculation():
    strand = tipseqhunter_parser.calculate_orientation(0, 0, 1, 0, 10)
    assert strand == '+'


def test_reverse_strand_orientation_calculation():
    strand = tipseqhunter_parser.calculate_orientation(0, 9, 10, 0, 10)
    assert strand == '-'


def test_orientation_calculation_with_central_clipping():
    strand = tipseqhunter_parser.calculate_orientation(0, 5, 5, 0, 10)
    assert strand == '+'


def test_data_extraction_from_repred(repred_dataframe):
    transposcope_df = tipseqhunter_parser.convert_dataframe(repred_dataframe)
    assert transposcope_df.shape == (10, 11)
