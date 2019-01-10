import os
import re


def load_vcf(file_path: str) -> str:
    with open(file_path, 'r') as fh:
        for line in fh.readlines():
            yield line.strip()


def parse_meta_info(melt_file_handler: str) -> dict:
    header = None
    meta_data = {}
    for line in melt_file_handler:
        if not line.startswith('##'):
            header = line[1:].split()
            break
        key, value = line[2:].split('=', 1)
        if key not in meta_data:
            meta_data[key] = {}
        if value.startswith('<'):
            data = re.search(r'ID=([^,]+)', value.strip('<>'))
            current_id = data.group(1)
            meta_data[key][current_id] = {}
            chrom_length = re.search(r'length=([^,]+)', value.strip('<>'))
            if chrom_length:
                meta_data[key][current_id]['length'] = chrom_length.group(1)
            description = re.search(r'Description="([^"]+)', value.strip('<>'))
            if description:
                meta_data[key][current_id]['Description'] = description.group(1)
            number = re.search(r'Number=([^,]+)', value.strip('<>'))
            if number:
                meta_data[key][current_id]['Number'] = number.group(1)
            data_type = re.search(r'Type=([^,]+)', value.strip('<>'))
            if data_type:
                meta_data[key][current_id]['Type'] = data_type.group(1)
        else:
            meta_data[key] = value

    return meta_data


if __name__ == '__main__':
    print(os.getcwd())
    for row in load_vcf('./test/parsers/examples/melt.vcf'):
        print(row)
