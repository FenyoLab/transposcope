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
git push
```

5. Set up GitHub pages to view the output
https://help.github.com/en/articles/configuring-a-publishing-source-for-github-pages#enabling-github-pages-to-publish-your-site-from-master-or-gh-pages


