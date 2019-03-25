# TranspoScope
### A Tool for Interactive Visualization of Evidence of Retrotransposon Insertions

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
### Generating Plots

```console
transposcope align <index> <bam> <me_reference> <host_reference> <sample_id>
```
input:          Input table
bam:            Bam file containing reads
me_reference:   The reference sequence of the mobile element being evaluated
host_reference: A folder containing the reference sequences for the host genome chromosomes E.G. HG38/
sample_id:      Unique identifier for the output to avoid overwriting previous output


There are additional optional parameters which can be viewed by passing the help flag.
```console
transposcope align --help
```

### Viewing Plots

```console
transposcope view path/to/alignment/output/web
```

### Notes

### Troubleshooting

