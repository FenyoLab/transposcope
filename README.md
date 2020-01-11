# TranspoScope
### A Tool for Interactive Visualization of Evidence of Retrotransposon Insertions

Transposcope is a package that is used to evaluate potential retrotransposon insertions, which have been identified by either MELT or TIPseqHunter (A generic input type will be added in later releases).

As novel insertions are not present within the reference genome, reads are unable to be aligned correctly. TranspoScope solves this problem by creating a localized reference sequence that matches what was proposed by either MELT or TIPseqHunter. Reads which aligned to regions flanking the novel insertion are then realigned to the localized sequence.

TranspoScope includes functionality to visualize and assess the realigned regions within a web-based visualization.

## Installation instructions 

### Install and Configure Anaconda / Miniconda
1. If Anaconda is not currently installed, install Miniconda using the installer and instructions available here, https://docs.conda.io/en/latest/miniconda.html#miniconda. 
2. Set up the Bioconda channels as described in the following link, https://bioconda.github.io/#set-up-channels.

### Create a Conda Environment and Install TranspoScope
Run the following command in the terminal:
```console
conda create -n transposcope_env python=3.7 transposcope
```
This command will create a new conda environment called 'transposcope_env' which uses Python 3.7 and includes the transposcope package.

Alternatively, TranspoScope can be installed into the current conda environment using the following command.
```console
conda install transposcope
```

### For more detailed usage instructions and examples, please use the Wiki.
https://github.com/FenyoLab/transposcope/wiki


## Examples
#### TIPseq Examples
##### An example showing strong evidence of an insertion
This example shows strong evidence as there are ~800 bridging reads where one read aligns with the reference sequence, and the pair aligns with the LINE-1 reference.


[![Likely Insertion](https://github.com/FenyoLab/transposcope/wiki//images/tipseq_likely_insertion.png)](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/melt_full?locus=chr1-113888412)

[Interactive visualization link](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/tipseq_test?locus=chr1-113888412)


##### An example showing less evidence of the insertion being real
This example is more difficult to classify as there are only one bridging reads and 10 junction reads supporting the insertion.

[![Likely Insertion](https://github.com/FenyoLab/transposcope/wiki/images/tipseq_unlikely_insertion.png)](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/tipseq_test?locus=chr1-121142693)

[Interactive visualization link](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/melt_full?locus=chr1-121142693)


#### Whole Genome Sequencing Examples
##### An example showing strong evidence of an insertion
This example shows strong evidence of there being an insertion. There are many bridging reads on both the 3' and 5' ends of the insertion, as well as many junction reads, which match the proposed LINE-1 reference sequence.

[![Likely Insertion](https://github.com/FenyoLab/transposcope/wiki//images/wgs_likely_insertion.png)](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/melt_full?locus=chr11-94951204)

[Interactive visualization link](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/melt_full?locus=chr11-94951204)

##### An example showing almost no evidence of an insertion
This example shows little evidence that there really is an insertion at this locus. Junction reads on the 5' flanking side match 3 bases of the proposed LINE-1 reference sequence with no other matches.

[![Likely Insertion](https://github.com/FenyoLab/transposcope/wiki//images/wgs_unlikely_insertion.png)](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/melt_full?locus=chr2-159882972)

[Interactive visualization link](https://fenyolab.github.io/transposcope_ui/#/dashboard/ungrouped/ungrouped/melt_full?locus=chr2-159882972)
