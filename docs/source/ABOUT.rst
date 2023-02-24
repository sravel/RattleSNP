.. image:: _images/rattleSNP_logo.png
   :target: _images/rattleSNP_logo.png
   :align: center
   :alt: RattleSNP Logo

How used the best SNP calling workflow for GBS or full genome sequencing !!!!

.. contents:: Table of Contents
   :depth: 2
   :backlinks: entry

From fastq to bam
-----------------

RattleSNP is a really flexible tool mapped paired data. You can give parameters on the *config.yaml* file to RattleSNP to generate a modular, dedicated pipeline for your own data.


Mapping
.......

RattleSNP includes (at the moment) only BWA tools.

Included tools :

* BWA_MEM http://bio-bwa.sourceforge.net/bwa.shtml
* BWA_SAMPE  http://bio-bwa.sourceforge.net/bwa.shtml


Optional statistics
........................

Using RattleSNP you can activate or deactivate statistics on mapping steps.

Directed acyclic graphs (DAGs) show the differences between deactivated (BUILD_STATS=False):

.. image:: _images/schema_pipeline_global-NOBUILD_STATS.png
   :target: _images/schema_pipeline_global-NOBUILD_STATS.png
   :alt: BUILD_STATS_FALSE

and activated BUILD_STATS step on configuration file (BUILD_STATS=True):

.. image:: _images/schema_pipeline_global-BUILD_STATS.png
   :target: _images/schema_pipeline_global-BUILD_STATS.png
   :alt: BUILD_STATS_TRUE

.. warning::
    In any case, MAPPING will be activated if BUILD_STATS is True even if MAPPING-ACTIVATE is False


SNP calling
-----------

The SNP calling is perform by GATK tools.

Included tools :

* GATK version >= 4.0.0 https://gatk.broadinstitute.org/hc/en-us/articles/360036194592-Getting-started-with-GATK4

.. image:: _images/schema_pipeline_global-SNPCALLING.png
   :target: _images/schema_pipeline_global-SNPCALLING.png
   :alt: SNPCALLING



Filter VCF and genetics tools
-----------------------------

.. image:: _images/schema_pipeline_global-FILTER.png
   :target: _images/schema_pipeline_global-FILTER.png
   :alt: FILTER
