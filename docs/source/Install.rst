.. contents:: Table of Contents
   :depth: 2
   :backlinks: entry

Requirements
============

RattleSNP requires |PythonVersions|, |SnakemakeVersions| and |graphviz|.

RattleSNP has been mostly developed to work on an HPC but a local installation is also available.

------------------------------------------------------------------------

Steps for HPC installation
==========================

As RattleSNP uses many tools, you must install them through one possibility:

1. Using the ``module load`` mode,

Let's check steps for **HPC installation** :

First install rattleSNP python package with pip.

.. code-block:: bash

   python3 -m pip install rattleSNP
   rattleSNP --help

Then run the command line to install on HPC

.. code-block:: bash

   rattleSNP install_cluster --help
   rattleSNP install_cluster --scheduler slurm --env modules --bash_completion --create_envmodule --modules_dir /path/to/dir/rattleSNP/

the script uses the snakemake profiles to build the installation profile for rattleSNP.
if --env is singularity, rattleSNP download images.
Then, the script proposes to modify the following files to adapt to your system achitecture


1. Adapt the :file:`cluster_config.yaml` file to manage cluster resources such as partition, memory and threads available for each job.
See the section :ref:`1. Preparing *cluster_config.yaml*` for further details.

2. Create a *snakemake profile* to configure cluster options.
See the section :ref:`2. Snakemake profiles` for details.

3. Adapt the file :file:`tools_path.yaml` - in YAML (Yet Another Markup Language) - format  to indicate to RattleSNP where the tools are installed.
See the section :ref:`3. How to configure tools_path.yaml` for details.


1. Preparing *cluster_config.yaml*
----------------------------------

In the ``cluster_config.yaml`` file, you can add partition, memory and threads to be used by default or specifically for each rule/tool.


.. warning::
    If more memory or threads are requested, please adapt the content of this file before running on your cluster.

Here is a example of the configuration file we used on our `IFB HPC <../../cluster_config.yaml>`_ .

A list of rules names can be found in the section :ref:`Threading rules inside rattleSNP`

.. warning::
    Please give to *cluster_config.yaml* specific parameters to rules get_versions and rule_graph without using wildcards into log files.


2. Snakemake profiles
---------------------

The Snakemake-profiles project is an open effort to create configuration profiles allowing to execute Snakemake in various computing environments
(job scheduling systems as Slurm, SGE, Grid middleware, or cloud computing), and available at https://github.com/Snakemake-Profiles/doc.

In order to run RattleSNP on HPC cluster, we use profiles.

Quickly, here is an example of the Snakemake SLURM profile we use for the French national bioinformatics infrastructure at IFB.
We followed the documentation found here https://github.com/Snakemake-Profiles/slurm#quickstart.

Now, your basic profile is created. To finalize it, change the ``RattleSNP/profiles/RattleSNP/config.yaml`` to :

.. code-block:: ini

    restart-times: 0
    jobscript: "slurm-jobscript.sh"
    cluster: "slurm-submit.py"
    cluster-status: "slurm-status.py"
    max-jobs-per-second: 1
    max-status-checks-per-second: 10
    local-cores: 1
    jobs: 200                   # edit to limit number jobs submit
    latency-wait: 60000000
    use-envmodules: true        # Adapt True/False only active one
    use-singularity: false      # if False, please install all R package on tools_config.yaml ENVMODULE/R
    rerun-incomplete: true
    printshellcmds: true


.. note::
   You can find the generated files when profiles are created following this documentation. IFB profile example can be found on the `̀ default_profile/`` repertory on our github repository.

3. How to configure tools_path.yaml
-----------------------------------

In the ``tools_path.yaml`` file, you can find sections MODULES. In order to fill it correctly fill this section with modules available on your cluster (here is an example):

.. literalinclude:: ../../rattleSNP/install_files/tools_path.yaml
    :language: YAML

.. warning::
    The use of MODULES is constraint with the use the *--use-envmodules* parameter in the snakemake command line.
    More details can be found here: https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#using-environment-modules


------------------------------------------------------------------------

Threading rules inside rattleSNP
--------------------------------

Please find here the rules names found in RattleSNP code.
It could be useful to set threads in local running using the snakemake command or in the cluster configuration to manage cluster resources.
This would save the user a painful exploration of the snakefiles code of RattleSNP.

.. code-block:: python

    bwa_index
    run_atropos
    run_fastqc
    bwa_mem_sort_bam
    run_bwa_aln
    bwa_sampe_sort_bam
    samtools_index
    samtools_idxstats
    merge_idxstats
    samtools_depth
    bam_stats_to_csv
    merge_bam_stats
    report
    picardTools_mark_duplicates
    create_sequence_dict
    create_sequence_fai
    gatk_HaplotypeCaller
    gatk_GenomicsDBImport
    gatk_GenotypeGVCFs_merge
    bcftools_concat
    vcftools_filter
    vcf_to_fasta
    vcf_to_geno
    vcf_stats
    report_vcf
    run_raxml
    run_raxml_ng



.. |PythonVersions| image:: https://img.shields.io/badge/python-3.7%2B-blue
   :target: https://www.python.org/downloads
   :alt: Python 3.7+

.. |SnakemakeVersions| image:: https://img.shields.io/badge/snakemake-≥5.10.0-brightgreen.svg?style=flat
   :target: https://snakemake.readthedocs.io
   :alt: Snakemake 5.10.0+

.. |graphviz| image:: https://img.shields.io/badge/graphviz-%3E%3D2.40.1-green
   :target: https://graphviz.org/
   :alt: graphviz 2.40.1+
