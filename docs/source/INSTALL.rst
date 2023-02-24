.. contents:: Table of Contents
   :depth: 2
   :backlinks: entry
   :local:

Requirements
============

RattleSNP requires |PythonVersions|, |SnakemakeVersions| and |graphviz|.

RattleSNP is developed to work mostly on an HPC distributed cluster but a local, single machine, installation is also possible.

------------------------------------------------------------------------

Install RattleSNP PyPI package
===============================

First, install the RattleSNP python package with pip.

.. code-block:: bash

   python3 -m pip install rattleSNP
   rattleSNP --help

Now, follow this documentation according to what you want, local or HPC mode.

------------------------------------------------------------------------

Steps for LOCAL installation
============================

Install RattleSNP in a *local* (single machine) mode using ``rattleSNP install_local`` command line.

.. click:: rattleSNP.main:main
    :prog: rattleSNP
    :commands: install_local
    :nested: full
    :hide-header:

#:hide-header:

To create a pipeline, tools used by RattleSNP are wrapped into ``Singularity images``. These images are automatically downloaded and used by the configuration files of the pipeline. Local mode install, without scheduler, is constrains to use these Singularity images.

the script uses the snakemake profiles to build the installation profile for rattleSNP.
if --env is singularity, rattleSNP download images.
Then, the script proposes to modify the following files to adapt to your system achitecture

Optionally (but recommended), after installing in local, you can check the RattleSNP installation using a dataset scaled for single machine.
See the section :ref:`Check install` for details.

------------------------------------------------------------------------

Steps for HPC distributed cluster installation
==============================================

RattleSNP uses any available snakemake profiles to ease cluster installation and resources management.
Run the command `rattleSNP install_cluster` to install on a HPC cluster.
We tried to make cluster installation as easy as possible, but it is somehow necessary to adapt a few files according to your cluster environment.

.. click:: rattleSNP.main:main
    :prog: rattleSNP
    :commands: install_cluster
    :nested: full
    :hide-header:

1. Adapt `profile` and `cluster_config.yaml`
---------------------------------------------

Now that RattleSNP is installed, it proposes default configuration files, but they can be modified. Please check and adapt these files to your own system architecture.

1. Adapt the pre-formatted `f –env si`snakemake profile`` to configure your cluster options.
See the section :ref:`1. Snakemake profiles` for details.

2. Adapt the :file:`cluster_config.yaml` file to manage cluster resources such as partition, memory and threads available for each job.
See the section :ref:`2. Adapting *cluster_config.yaml*` for further details.


2. Adapt `tools_path.yaml`
--------------------------

As RattleSNP uses many tools, you must install them using one of the two following possibilities:

1. Either through the |Singularity| containers,

2. Or using the ``module load`` mode,

.. code-block:: bash

   rattleSNP install_cluster --help
   rattleSNP install_cluster --scheduler slurm --env modules
   # OR
   rattleSNP install_cluster --scheduler slurm --env singularity

If ``--env singularity`` argument is specified, RattleSNP will download previously build Singularity images, containing the complete environment need to run RattleSNP (tools and dependencies).

Adapt the file :file:``tools_path.yaml`` - in YAML (Yet Another Markup Language) - format  to indicate RattleSNP where the different tools are installed on your cluster.
See the section :ref:`3. How to configure tools_path.yaml` for details.


------------------------------------------------------------------------

Check install
==============

In order to test your install of RattleSNP, a data test called ``data_test_rattleSNP/`` is available at http://nas-bgpi.myds.me/DOC/rattleSNP/data_test_rattleSNP.zip.

.. click:: rattleSNP.main:main
    :prog: rattleSNP
    :commands: test_install
    :nested: full
    :hide-header:

This dataset will be automatically downloaded by RattleSNP in the ``-d`` repertory using :

.. code-block:: bash

   rattleSNP test_install -d test

Launching the (suggested, to be adapted) command line in CLUSTER mode will perform the tests:

.. code-block:: bash

   rattleSNP run_cluster --config test/data_test_config.yaml

In local mode, type :

.. code-block:: bash

   rattleSNP run_local -t 8 -c test/data_test_config.yaml --singularity-args "--bind $HOME"


------------------------------------------------------------------------

Advance installation
====================


1. Snakemake profiles
---------------------

The Snakemake-profiles project is an open effort to create configuration profiles allowing to execute Snakemake in various computing environments
(job scheduling systems as Slurm, SGE, Grid middleware, or cloud computing), and available at https://github.com/Snakemake-Profiles/doc.

In order to run RattleSNP on HPC cluster, we take advantages of profiles.

Quickly, see `here <https://github.com/SouthGreenPlatform/rattleSNP/blob/master/rattleSNP/install_files/cluster_config_SLURM.yaml>`_ an example of the Snakemake SLURM profile we used for the French national bioinformatics infrastructure at IFB.

More info about profiles can be found here https://github.com/Snakemake-Profiles/slurm#quickstart.

Preparing the profile's *config.yaml* file
******************************************

Once your basic profile is created, to finalize it, modify as necessary the ``rattleSNP/rattleSNP/default_profile/config.yaml`` to customize Snakemake parameters that will be used internally by RattleSNP:

.. code-block:: ini

   restart-times: 0
   jobscript: "slurm-jobscript.sh"
   cluster: "slurm-submit.py"
   cluster-status: "slurm-status.py"
   max-jobs-per-second: 1
   max-status-checks-per-second: 10
   local-cores: 1
   jobs: 200                   # edit to limit the number of jobs submitted in parallel
   latency-wait: 60000000
   use-envmodules: true        # adapt True/False for env of singularuty, but only active one possibility !
   use-singularity: false      # if False, please install all R packages listed in tools_config.yaml ENVMODULE/R
   rerun-incomplete: true
   printshellcmds: true


2. Adapting *cluster_config.yaml*
----------------------------------

In the ``cluster_config.yaml`` file, you can manage HPC resources, choosing partition, memory and threads to be used by default,
or specifically, for each rule/tool depending on your HPC Job Scheduler (see `there <https://snakemake.readthedocs.io/en/latest/snakefiles/configuration.html#cluster-configuration-deprecated>`_). This file generally belongs to a Snakemake profile (see above).

.. warning::
   If more memory or threads are requested, please adapt the content
   of this file before running on your cluster.


A list of RattleSNP rules names can be found in the section :ref:`Threading rules inside rattleSNP`


.. warning::
   For some rules in the *cluster_config.yaml* as `rule_graph` or `run_get_versions`,
   we use by default wildcards, please don't remove it.


3. How to configure tools_path.yaml
-----------------------------------

In the ``tools_path`` file, you can find two sections: SINGULARITY and ENVMODULES. In order to fill it correctly, you have 2 options:

1. Use only SINGULARITY containers: in this case, fill only this section. Put the path to the built Singularity images you want to use.
Absolute paths are strongly recommended. See the section :ref:`'How to build singularity images'<How to build singularity images>`  for further details.

.. literalinclude:: ../../rattleSNP/install_files/tools_path.yaml
   :language: YAML
   :lines: 6-8

.. warning::
   To ensure SINGULARITY containers to be really used, one needs to make
   sure that the *--use-singularity* flag is included in the snakemake command line.


2. Use only ENVMODULES: in this case, fill this section with the modules available on your cluster (here is an example):

.. literalinclude:: ../../rattleSNP/install_files/tools_path.yaml
   :language: YAML
   :lines: 10-18

RattleSNP needs a wide set of R modules for reporting. If you use ENVMODULE R, just have a look at dependencies in the ``Containers/Singularity.report.def`` file.
Yes, plenty of packages!! That's why we provide build Singularity containers ready to use and recommend them for the R part.

.. note::
   TIP !! We provide a Singularity container for all R packages (Singularity.report.def),
   thus you can use this one to create a dedicated module environment.


.. warning::
   Make sure to specify the *--use-envmodules* flag in the snakemake command
   line for ENVMODULE to be implemented.
   More details can be found here:
   https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#using-environment-modules


------------------------------------------------------------------------

And more ...
-------------

How to build Singularity images
*******************************

You can build your own image using the available *.def* recipes from the ``rattleSNP/rattleSNP/containers/`` directory.

.. warning::
   Be careful, you need root access to build Singularity images

.. code-block:: bash

   cd rattleSNP/rattleSNP/containers/
   sudo make build

Threading rules inside RattleSNP
********************************

Please find here the rules names found in RattleSNP code.
It is recommended to set threads using the snakemake command when running on a single machine,
or in a cluster configuration file to manage cluster resources through the job scheduler.
This would save users a painful exploration of the snakefiles of RattleSNP.

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



.. |PythonVersions| image:: https://img.shields.io/badge/python-3.8%2B-blue
   :target: https://www.python.org/downloads
   :alt: Python 3.8+

.. |SnakemakeVersions| image:: https://img.shields.io/badge/snakemake-≥5.10.0-brightgreen.svg?style=flat
   :target: https://snakemake.readthedocs.io
   :alt: Snakemake 5.10.0+

.. |Singularity| image:: https://img.shields.io/badge/singularity-≥3.3.0-7E4C74.svg
   :target: https://sylabs.io/docs/
   :alt: Singularity 3.10.0+

.. |graphviz| image:: https://img.shields.io/badge/graphviz-%3E%3D2.40.1-green
   :target: https://graphviz.org/
   :alt: graphviz 2.40.1+
