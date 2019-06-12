# TranspoScope
### A Tool for Interactive Visualization of Evidence of Retrotransposon Insertions

#### Examples
##### An example showing strong evidence of an insertion
This example shows strong evidence as there are ~100 bridging reads where one read aligns to the reference sequence and the pair aligns to the LINE-1 reference.
http://openslice.fenyolab.org/transposcope/transpoScope.html?area=pancreatic&patientFolder=A31&type=A31-Normal#chrX-81746649(1)

##### An example showing little evidence of the insertion being real
This example does not show much evidence of the insertion being real as there are only three bridging reads. In addition, many of the reads which match the LINE-1 reference sequence do not have a pair which matches the reference genome.
http://openslice.fenyolab.org/transposcope/transpoScope.html?area=pancreatic&patientFolder=A31&type=A31-Normal#chr6-37876353(5)

## Installation instructions 

### Install and Configure Anaconda / Miniconda
1. If Anaconda is not currently installed, install Miniconda using the installer and instructions available here, https://docs.conda.io/en/latest/miniconda.html#miniconda. (Python 2 is being retired on the 1st of January 2020.  It is, therefore, preferable to use the Python 3 installer).
2. Set up the Bioconda channels as described in the following link, https://bioconda.github.io/#set-up-channels.

### Create a Conda Environment and Install TranspoScope
Run the following command in the terminal:
```console
conda create -n transposcope_env python=3.6 transposcope
```
This command will create a new conda environment called 'transposcope_env' which uses Python 3.6 and includes the transposcope package.

Alternatively, transposcope can be installed into the current conda environment using the following command.
```console
conda install transposcope
```
## General Use
### Generating Plots

```console
transposcope align <index> <bam> <me_reference> <host_reference> <sample_id>
```
| Input | Discription |
|-|-|
|index         | Index table|
|bam           | Bam file containing reads|
|me_reference  | The reference sequence of the mobile element being evaluated|
|host_reference| A folder containing the reference sequences for the host genome chromosomes E.G. HG38/|
|sample_id     | Unique identifier for the output to avoid overwriting previous output|


There are additional optional parameters which can be viewed by passing the help flag.
```console
transposcope align --help
```

### Viewing Plots

```console
transposcope view path/to/alignment/output/web
```

### Publishing Plots to GitHub

1. Create a new repository on GitHub.
https://help.github.com/en/articles/creating-a-new-repository

2. Initialize git in the web folder output from the align step.
```console
cd <path/to/alignment/output/web>
git init
git add .
git commit -m 'commiting generated plots'
```

3. Link the Github repository created in **step 1** to your local git folder
```console
git remote add origin <<https://github.com/user/repo.git>>
```

4. Push the local folder to Github
```console
git push origin master
```

5. Set up GitHub pages to view the output
https://help.github.com/en/articles/configuring-a-publishing-source-for-github-pages#enabling-github-pages-to-publish-your-site-from-master-or-gh-pages

### Example files
A zip archive containing example files can be downloaded from the following link [example.tar.gz](https://github.com/FenyoLab/transposcope/files/3013885/example.tar.gz)

```
example
├── bam
│   ├── example.bam
│   └── example.bam.bai
├── index_table.tab
└── reference
    ├── hg19
    │   └── chr22.fa
    ├── Homo_sapiens_L1.L1HS.fa
    └── Homo_sapiens_L1.L1HS.fa.fai
```
| Filename | Description |
|-|-|
|index_table.tab| Defines the regions flanking the insertions|
|/reference/Homo_sapiens_L1.L1HS.fa| reference sequence for the mobile element|
|/reference/Homo_sapiens_L1.L1HS.fa.fai| FASTA index file|
|/reference/hg19/chr22.fa| This example only contains insertions in chromosome 22|
|/bam/example.bam| bam file containing reads aligned to the hg19 reference genome|
|/bam/example.bam.bai| BAM index file|

---

To run TranspoScope using the example files, first install TranspoScope. Next, download the example archive and navigate to the directory in which the file was downloaded, then:

1. Extract the files
```console
tar -zxvf example.tar.gz
```
2. Navigate to the extracted directory
```console
cd example
```
3. Run TranspoScope align
```console
transposcope align index_table.tab bam/example.bam reference/Homo_sapiens_L1.L1HS.fa reference/hg19/ example
```
4. Two folders will be created, 'output' and 'web'. To view the coverage using the viewer run:
```console
transposcope view web
```
5. To stop the viewer press ctrl+c when the terminal window is selected

## Notes
### Index Table
The index table is a tab delimited file which defines attributes associated with each potential insertion. Each row outlines an insertion through eleven variables.

|Attribute | Meaning|
| - | - |
|chromosome        |The chromosome in which the insertion is located|
|target_start      |The start coordinate of the region flanking the insertion|
|target_end        |The end coordinate of the region flanking the insertion|
|clip_start        |The coordinate where reads begin to be soft clipped due to the insertion|
|clip_end          |The coordinate where the mobile element sequence begins|
|strand            |Whether the mobile element should be reverse complemented|
|pred              |The predicted confidence of the insertion being real|
|three_prime_end   |True when the target region flanks the 3' end of the mobile element, false when it flanks the 5' end|
|enzyme_cut_sites  |The coordinates of enzyme cut sites to be shown in the visualization and uses the following structure description-offset_from_insertion_site. Multiple sites are delimited using a ':'|
|me_start          |The start coordinate of the mobile element in relation of its reference sequence (5094 for TIPseq)|
|me_end            |The end coordinate of the mobile element in relation of its reference sequence (6064 for TIPseq)|
