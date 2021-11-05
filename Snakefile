#!/usr/bin/env snakemake
# -*- coding: utf-8 -*-

from pathlib import Path
import pprint
from snakemake.logging import logger

# load own functions
import rattleSNP
from rattleSNP.module import parse_idxstats, check_mapping_stats, merge_bam_stats_csv
from rattleSNP.module import RattleSNP

# GLOBAL VARIABLES
pp = pprint.PrettyPrinter(indent=4)

# recovery basedir where RattleSNP was installed
# logger.info(rattleSNP.description_tools)

# pp(workflow.basedir)
rattlesnp = RattleSNP(workflow, config)
tools_config = rattlesnp.tools_config
cluster_config = rattlesnp.cluster_config

# print(rattlesnp.export_use_yaml)
# print for debug:
# logger.debug(rattlesnp)
# exit()
# print(tools_config)

# exit()

###############################################################################
# dir and suffix
fastq_dir = config["DATA"]["FASTQ"]
bam_dir = config["DATA"]["BAM"]
vcf_dir = config["DATA"]["VCF"]
reference_file =  config["DATA"]["REFERENCE_FILE"]
basename_reference = Path(reference_file).stem
out_dir = config["DATA"]["OUTPUT"]
log_dir = f"{out_dir}LOGS/"

cleaning = config["CLEANING"]["ATROPOS"]
fastqc = config["FASTQC"]
SNPcalling =  config["SNPCALLING"]
build_stats =  config["MAPPING"]["BUILD_STATS"]



# to lunch separator
BWA_INDEX = ['amb','ann','bwt','pac','sa']

#*###############################################################################
#############################################
# use threads define in cluster_config rule or rule default or default in snakefile
#############################################
def get_threads(rule, default):
    """
    give threads or 'cpus-per-task from cluster_config rule : threads to SGE and cpus-per-task to SLURM
    """
    if rule in cluster_config and 'threads' in cluster_config[rule]:
        return int(cluster_config[rule]['threads'])
    elif rule in cluster_config and 'cpus-per-task' in cluster_config[rule]:
        return int(cluster_config[rule]['cpus-per-task'])
    elif '__default__' in cluster_config and 'cpus-per-task' in cluster_config['__default__']:
        return int(cluster_config['__default__']['cpus-per-task'])
    elif '__default__' in cluster_config and 'threads' in cluster_config['__default__']:
        return int(cluster_config['__default__']['threads'])
    if workflow.global_resources["_cores"]:
        return workflow.global_resources["_cores"]
    return default

def get_fastq_file():
    """return if file provide from cleaning or direct sample"""

    dico_mapping = {
                    "fasta": reference_file,
                     "index": rules.bwa_index.output.index
                    }
    if cleaning:
        dico_mapping.update({
                    "R1" : rules.run_atropos.output.R1,
                    "R2" : rules.run_atropos.output.R2
                })
    else:
        dico_mapping.update({
                    "R1" :f"{fastq_dir}{{samples}}_R1.fastq.gz",
                    "R2" : f"{fastq_dir}{{samples}}_R2.fastq.gz"
                })
    # print(dico_mapping)
    return dico_mapping

def output_final(wildcards):
    """FINAL RULE"""
    dico_final = {}
    if cleaning:
        dico_final.update({
                    "atropos_files_R1" : expand(rules.run_atropos.output.R1, samples = rattlesnp.samples),
                    "atropos_files_R2" : expand(rules.run_atropos.output.R2, samples = rattlesnp.samples),
                })
    if fastqc:
        dico_final.update({
                    "fastQC_files_R1": expand(rules.run_fastqc.output.R1,samples=rattlesnp.samples),
                    "fastQC_files_R2": expand(rules.run_fastqc.output.R2,samples=rattlesnp.samples),
        })
    if rattlesnp.mapping_activated:
        dico_final.update({
                    "bam": expand( f"{out_dir}1_mapping/{rattlesnp.mapping_tool_activated}/{{samples}}.bam.bai",samples=rattlesnp.samples),
        })
    if rattlesnp.mapping_stats_activated:
        dico_final.update({
            "html": expand(f"{out_dir}1_mapping/{rattlesnp.mapping_tool_activated}/{{samples}}.bam.bai",
                samples=rattlesnp.samples),
        })
    if build_stats:
        dico_final.update({
                    "report" : f"{out_dir}1_mapping/STATS/report.html",
                })
    if rattlesnp.calling_activated:
        dico_final.update({
                    "vcf_file": f'{out_dir}2_snp_calling/All_samples_GenotypeGVCFs_WITHOUT_MITO_raw.vcf.gz',
                    "report_vcf_raw": expand(f"{out_dir}3_all_snp_calling_stats/report_vcf{{vcf_suffix}}.html",vcf_suffix="_raw")
                })
    if rattlesnp.vcf_filter_activated:
        dico_final.update({
                    "report_vcf_filter": expand(f"{out_dir}3_all_snp_calling_stats/report_vcf{{vcf_suffix}}.html", vcf_suffix=config['PARAMS']['FILTER_SUFFIX']),
                    #"fasta": expand(f'{out_dir}5_fasta_file/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.fasta', vcf_suffix=config['PARAMS']['FILTER_SUFFIX'])
                    "geno" :  expand(f'{out_dir}7_geno_file/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.geno', vcf_suffix=config['PARAMS']['FILTER_SUFFIX'])
                })
    if rattlesnp.vcf_path:
        dico_final.update({
                    "report_vcf_user": expand(f"{out_dir}3_all_snp_calling_stats/report_vcf{{vcf_suffix}}.html", vcf_suffix="_user")
                })
    if rattlesnp.run_RAXML:
        dico_final.update({
                    "RAXML": expand(f'{out_dir}6_raxml/filter{{vcf_suffix}}/RAxML_bestTree.All_samples_GenotypeGVCFs_filter{{vcf_suffix}}', vcf_suffix=config['PARAMS']['FILTER_SUFFIX'])
                })
    if rattlesnp.run_RAXML_NG:
        dico_final.update({
                    "RAXML_NG": expand(f'{out_dir}6_raxml_ng/filter{{vcf_suffix}}/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.raxml.bestTree', vcf_suffix=config['PARAMS']['FILTER_SUFFIX'])
                })
    # pp.pprint(dico_final)
    return dico_final


# --- Main Build Rules --- #
rule final:
    """construct a table of all resume files"""
    input:
        unpack(output_final)

rule bwa_index:
    """make index with bwa for reference file"""
    threads: get_threads('bwa_index', 1)
    input:
            fasta = reference_file
    output:
            index = expand(f'{reference_file}.{{suffix}}',suffix=BWA_INDEX)
    log :
            error =  f'{log_dir}bwa_index/{basename_reference}.e',
            output = f'{log_dir}bwa_index/{basename_reference}.o'
    message:
            f"""
             Running {{rule}}
                Input:
                    - Fasta : {{input.fasta}}
                Output:
                    - sa_file: {{output.index}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
            tools_config["MODULES"]["BWA"]
    shell:
            """
                bwa index {input.fasta} 1>{log.output} 2>{log.error}
            """

# 1=atropos
rule run_atropos:
    """Run atropos for cleaning data"""
    threads: get_threads('run_atropos', 2)
    input:
            R1 = f"{fastq_dir}{{samples}}_R1.fastq.gz",
            R2 = f"{fastq_dir}{{samples}}_R2.fastq.gz"
    output:
            R1 = f"{out_dir}0_cleaning/ATROPOS/{{samples}}_R1_ATROPOS.fastq.gz",
            R2 = f"{out_dir}0_cleaning/ATROPOS/{{samples}}_R2_ATROPOS.fastq.gz"
    params:
            other_options = config["PARAMS_TOOLS"]["ATROPOS"]
    log :
            error =  f'{log_dir}run_atropos/{{samples}}.e',
            output = f'{log_dir}run_atropos/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fastq R1 : {{input.R1}}
                    - Fastq R2 : {{input.R2}}
                Output:
                    - Fastq R1 : {{output.R1}}
                    - Fastq R2 : {{output.R2}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["ATROPOS"]
    shell:
        """
            atropos trim --threads {threads} {params.other_options} -o {output.R1} -p {output.R2} -pe1 {input.R1} -pe2 {input.R2}  1>{log.output} 2>{log.error}
        """

rule run_fastqc:
    """Run fastqc for control data"""
    threads: get_threads('run_fastqc', 1)
    input:
            R1 = rules.run_atropos.output.R1 if cleaning else f"{fastq_dir}{{samples}}_R1{rattlesnp.fastq_files_ext}",
            R2 = rules.run_atropos.output.R2 if cleaning else f"{fastq_dir}{{samples}}_R2{rattlesnp.fastq_files_ext}"
    output:
            R1 = f"{out_dir}0_cleaning/FASTQC/{{samples}}_R1{rattlesnp.cleaning_tool}_fastqc.html",
            R2 = f"{out_dir}0_cleaning/FASTQC/{{samples}}_R2{rattlesnp.cleaning_tool}_fastqc.html"
    params:
            outdir = directory(f"{out_dir}0_cleaning/FASTQC/"),
            other_options = config["PARAMS_TOOLS"]["FASTQC"]
    log :
            error =  f'{log_dir}run_fastqc_PE/{{samples}}.e',
            output = f'{log_dir}run_fastqc_PE/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fastq R1 : {{input.R1}}
                    - Fastq R2 : {{input.R2}}
                Output:
                    - html R1 : {{output.R1}}
                    - html R2 : {{output.R2}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["FASTQC"]
    shell:
            """
                fastqc -t {threads} {params.other_options} -o {params.outdir} {input.R1} {input.R2}  1>{log.output} 2>{log.error}
            """


rule bwa_mem_sort_bam:
    """make bwa mem for all samples on reference"""
    threads: get_threads('bwa_mem_sort_bam', 1)
    input:
            **get_fastq_file()
    output:
            bam_file =  f"{out_dir}1_mapping/BWA_MEM/{{samples}}.bam"
    params:
            rg = f"@RG\\tID:{{samples}}\\tSM:{{samples}}\\tPL:Illumina",
            other_options_bwa = config["PARAMS_TOOLS"]["BWA_MEM"],
            other_options_samtools_view = config["PARAMS_TOOLS"]["SAMTOOLS_VIEW"],
            other_options_samtools_sort = config["PARAMS_TOOLS"]["SAMTOOLS_SORT"]
    log:
            error =  f'{log_dir}bwa_mem_sort_bam/{{samples}}.e',
            output = f'{log_dir}bwa_mem_sort_bam/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fasta : {{input.fasta}}
                    - R1: {{input.R1}}
                    - R2: {{input.R2}}
                Output:
                    - Bam: {{output.bam_file}}
                Params:
                    - other_options_bwa: {{params.other_options_bwa}}
                    - other_options_samtools_view: {{params.other_options_samtools_view}}
                    - other_options_samtools_sort: {{params.other_options_samtools_sort}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["BWA"],
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
        """
                (bwa mem -t {threads} {input.fasta} {input.R1} {input.R2} -R '{params.rg}' |
                samtools view -@ {threads} {params.other_options_samtools_view} |
                samtools sort -@ {threads} {params.other_options_samtools_sort} -o {output.bam_file} ) 1>{log.output} 2>{log.error}
        """


rule run_bwa_aln:
    """make bwa aln for all samples PE on reference"""
    threads: get_threads('run_bwa_aln_PE', 1)
    input:
            fasta = reference_file,
            index = rules.bwa_index.output.index,
            R1 = f"{fastq_dir}{{samples}}_R1.fastq.gz" if not cleaning else rules.run_atropos.output.R1 ,
            R2 = f"{fastq_dir}{{samples}}_R2.fastq.gz" if not cleaning else rules.run_atropos.output.R2
    output:
            sai_R1 = temp(f"{out_dir}1_mapping/BWA_SAMPE/{{samples}}_R1.BWAALN.sai"),
            sai_R2 = temp(f"{out_dir}1_mapping/BWA_SAMPE/{{samples}}_R2.BWAALN.sai")
    params:
            other_options = config["PARAMS_TOOLS"]["BWA_ALN"]
    log:
            error =  f'{log_dir}run_bwa_aln_PE/{{samples}}.e',
            output = f'{log_dir}run_bwa_aln_PE/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fasta : {{input.fasta}}
                    - R1: {{input.R1}}
                    - R2: {{input.R2}}
                Output:
                    - sai R1: temp({{output.sai_R1}})
                    - sai R2: temp({{output.sai_R2}})
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["BWA"],
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
            """
                bwa aln -t {threads} {params.other_options} -f {output.sai_R1} {input.fasta} {input.R1} 1>{log.output} 2>{log.error} &&
                bwa aln -t {threads} {params.other_options} -f {output.sai_R2} {input.fasta} {input.R2} 1>{log.output} 2>{log.error}
            """


rule bwa_sampe_sort_bam:
    """make bwa sampe for all samples PE on reference"""
    threads: get_threads('bwa_sampe_sort_bam', 1)
    input:
            fasta = reference_file,
            index = rules.bwa_index.output.index,
            R1 = rules.run_bwa_aln.input.R1,
            R2 = rules.run_bwa_aln.input.R2,
            sai_R1 = rules.run_bwa_aln.output.sai_R1,
            sai_R2 = rules.run_bwa_aln.output.sai_R2
    output:
            bam_file = f"{out_dir}1_mapping/BWA_SAMPE/{{samples}}.bam"
    params:
            rg = f"@RG\\tID:{{samples}}\\tSM:{{samples}}\\tPL:Illumina",
            other_options_bwa = config["PARAMS_TOOLS"]["BWA_SAMPE"],
            other_options_samtools_view = config["PARAMS_TOOLS"]["SAMTOOLS_VIEW"],
            other_options_samtools_sort = config["PARAMS_TOOLS"]["SAMTOOLS_SORT"]
    log:
            error =  f'{log_dir}bwa_sampe_sort_bam/{{samples}}.e',
            output = f'{log_dir}bwa_sampe_sort_bam/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fasta : {{input.fasta}}
                    - R1: {{input.R1}}
                    - R2: {{input.R2}}
                Output:
                    - Bam: {{output.bam_file}}
                Params:
                    - other_options_bwa: {{params.other_options_bwa}}
                    - other_options_samtools_view: {{params.other_options_samtools_view}}
                    - other_options_samtools_sort: {{params.other_options_samtools_sort}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["BWA"],
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
            """
                (bwa sampe -r"{params.rg}" {params.other_options_bwa} {input.fasta} {input.sai_R1} {input.sai_R2} {input.R1} {input.R2} |
                samtools view -@ {threads} {params.other_options_samtools_view} |
                samtools sort -@ {threads} {params.other_options_samtools_sort} -o {output.bam_file} ) 1>{log.output} 2>{log.error}
            """

rule samtools_index:
    """index bam for use stats"""
    threads: get_threads('samtools_index', 1)
    input:
            bam = f"{out_dir}1_mapping/{rattlesnp.mapping_tool_activated}/{{samples}}.bam"
    output:
            bai = f"{out_dir}1_mapping/{rattlesnp.mapping_tool_activated}/{{samples}}.bam.bai"
    log:
            error =  f'{log_dir}samtools_index/{{samples}}.e',
            output = f'{log_dir}samtools_index/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Bam : {{input.bam}}
                Output:
                    - Bai : {{output.bai}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
            """
                samtools index -@ {threads} {input.bam} 1>{log.output} 2>{log.error}
            """


####### Stats
rule samtools_idxstats:
    """apply samtools idxstats on all bam"""
    threads: get_threads('samtools_idxstats', 1)
    input:
            bam = rules.samtools_index.input.bam,
            bai = rules.samtools_index.output.bai
    output:
            txt_file = f"{out_dir}1_mapping/STATS/idxstats/{{samples}}_IDXSTATS.txt"
    log:
            error =  f'{log_dir}samtools_idxstats/{{samples}}.e',
            output = f'{log_dir}samtools_idxstats/{{samples}}.o'
    message:
            f"""
            Running {{rule}} for
                Input:
                    - Bam : {{input.bam}}
                Output:
                    - txt : {{output.txt_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
            """
                samtools idxstats -@ {threads} {input.bam} | tee {output.txt_file} 1>{log.output} 2>{log.error}
            """


rule merge_idxstats:
    """merge all samtools idxstats files"""
    threads : get_threads('merge_idxstats', 1)
    input :
            csv_resume = expand(rules.samtools_idxstats.output.txt_file , samples = rattlesnp.samples)
    output :
            csv_resume_merge = report(f"{out_dir}1_mapping/STATS/all_mapping_stats_resume.csv", category="Resume mapping info's")
    log:
            error =  f'{log_dir}merge_idxstats/all_mapping_stats_resume.e',
            output = f'{log_dir}merge_idxstats/all_mapping_stats_resume.o'
    message:
            f"""
            Running {{rule}} for
                Input:
                    - CSV_files : {{input.csv_resume}}
                Output:
                    - Merge CSV : {{output.csv_resume_merge}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    run :
        parse_idxstats(input.csv_resume, output.csv_resume_merge, sep="\t")

########################## STATS BAM
rule samtools_depth:
    """apply samtools depth on all bam SE end PE"""
    threads: get_threads('samtools_depth', 1)
    input:
            bam = rules.samtools_index.input.bam,
            bai = rules.samtools_index.output.bai
    output:
            txt_file = f"{out_dir}1_mapping/STATS/depth/{{samples}}_DEPTH.txt"
    params:
            other_options = config["PARAMS_TOOLS"]["SAMTOOLS_DEPTH"]
    log:
            error =  f'{log_dir}samtools_depth/{{samples}}.e',
            output = f'{log_dir}samtools_depth/{{samples}}.o'
    message:
            f"""
            Execute {{rule}} for
                Input:
                    - Bam : {{input.bam}}
                Output:
                    - txt : {{output.txt_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
            """
                samtools depth {params.other_options} {input.bam} | tee {output.txt_file} 1>{log.output} 2>{log.error}
            """

rule bam_stats_to_csv:
    """build csv with mean depth, median depth and mean coverage for all bam"""
    threads : get_threads('bam_stats_to_csv', 1)
    input :
            bam = rules.samtools_index.input.bam,
            bai = rules.samtools_index.output.bai,
            txt = rules.samtools_depth.output.txt_file
    output :
            csv_resume = temp(f'{out_dir}1_mapping/STATS/depth/{{samples}}.csv')
    log:
            error =  f'{log_dir}bam_stats_to_csv/{{samples}}.e',
            output = f'{log_dir}bam_stats_to_csv/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Bam : {{input.bam}}
                Output:
                    - CSV : temp({{output.csv_resume}})
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    run :
        check_mapping_stats(input.bam, output.csv_resume, sep="\t")

rule merge_bam_stats:
    """merge all bam_stats_to_csv files"""
    threads : get_threads('merge_bam_stats', 1)
    input :
            csv_resume = expand(rules.bam_stats_to_csv.output.csv_resume , samples = rattlesnp.samples)
    output :
            csv_resume_merge = report(f"{out_dir}1_mapping/STATS/all_mapping_stats_Depth_resume.csv", category="Resume mapping info's")
    log:
            error =  f'{log_dir}merge_bam_stats/mergeResume.e',
            output = f'{log_dir}merge_bam_stats/mergeResume.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - CSV list : {{input.csv_resume}}
                Output:
                    - CSV : temp({{output.csv_resume_merge}})
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    run :
        merge_bam_stats_csv(input.csv_resume, output.csv_resume_merge, sep="\t")



rule report:
    threads: get_threads('report', 1)
    input:
         depth_resume = rules.merge_bam_stats.output.csv_resume_merge,
         idxstats_resume = rules.merge_idxstats.output.csv_resume_merge
    output:
        report = f"{out_dir}1_mapping/STATS/report.html"
    log:
            error =  f'{log_dir}report/report.e',
            output = f'{log_dir}report/report.o'
    # envmodules:
        # tools_config["MODULES"]["R"]
    message:
            f"""
            Running {{rule}}
                Input:
                    - csv : {{input.depth_resume}}
                    - csv : {{input.idxstats_resume}}
                Output:
                    - report : {{output.report}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    script:
        """script/report.Rmd"""

###################################################################################
rule picardTools_mark_duplicates:
    """apply picardTools_mark_duplicates on all bam"""
    threads: get_threads('picardTools_mark_duplicates', 1)
    input:
            bam_file = rules.samtools_index.input.bam if rattlesnp.mapping_tool_activated else f"{rattlesnp.bam_path}{{samples}}.bam"
    output:
            bam_file = f"{out_dir}1_mapping/{rattlesnp.mapping_tool_activated}/mark-duplicates/{{samples}}_picardTools-mark-duplicates.bam",
            txt_file = f"{out_dir}1_mapping/{rattlesnp.mapping_tool_activated}/mark-duplicates/{{samples}}_picardTools-mark-duplicates.metrics"

    params:
            other_options = config["PARAMS_TOOLS"]["PICARDTOOLS_MARK_DUPLICATES"]
    log:
            error =  f'{log_dir}picardTools_mark_duplicates/{{samples}}.e',
            output = f'{log_dir}picardTools_mark_duplicates/{{samples}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Bam : {{input.bam_file}}
                Output:
                    - Bam : {{output.bam_file}}
                    - metric : {{output.txt_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["PICARDTOOLS"]
    shell:
        """
            picard MarkDuplicates {params.other_options} INPUT={input.bam_file} OUTPUT={output.bam_file} METRICS_FILE={output.txt_file} 1>{log.output} 2>{log.error}
        """


########################## SNP calling
rule create_sequence_dict:
    """create sequence dict for gatk_HaplotypeCaller reference"""
    threads: get_threads('create_sequence_dict', 1)
    input:
            reference = reference_file
    output:
            dict = reference_file.replace(".fasta",".dict")
    params:
            java_mem="8g"
    log:
            error =  f'{log_dir}create_sequence_dict/{basename_reference}.e',
            output = f'{log_dir}create_sequence_dict/{basename_reference}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fasta : {{input.reference}}
                Output:
                    - dict : {{output.dict}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["GATK4"]
    shell:
        """
            gatk CreateSequenceDictionary --java-options "-Xmx{params.java_mem}" -R {input.reference} 1>{log.output} 2>{log.error}
        """

rule create_sequence_fai:
    """create sequence fai for gatk_HaplotypeCaller reference"""
    threads: get_threads('create_sequence_fai', 1)
    input:
            reference = reference_file
    output:
            fai = reference_file.replace(".fasta",".fasta.fai")
    log:
            error =  f'{log_dir}create_sequence_fai/{basename_reference}.e',
            output = f'{log_dir}create_sequence_fai/{basename_reference}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Fasta : {{input.reference}}
                Output:
                    - fai : {{output.fai}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
        """
            samtools faidx {input.reference} 1>{log.output} 2>{log.error}
        """

rule gatk_HaplotypeCaller:
    """apply gatk_HaplotypeCaller on all bam SE end PE"""
    threads: get_threads('gatk_HaplotypeCaller', 1)
    input:
            bam_file = rules.picardTools_mark_duplicates.output.bam_file,
            reference = reference_file,
            dict = rules.create_sequence_dict.output.dict,
            fai = rules.create_sequence_fai.output.fai
    output:
            vcf_file = f"{out_dir}2_snp_calling/GATK_HaplotypeCaller/{{samples}}-{{chromosomes}}_GATK4.gvcf"
    params:
            java_mem="8g",                  # TODO add argument to cluster_config
            interval = "{chromosomes}",
            other_options = config["PARAMS_TOOLS"]["GATK_HAPLOTYPECALLER"]
    log:
            error =  f'{log_dir}gatk_HaplotypeCaller/{{samples}}_{{chromosomes}}.e',
            output = f'{log_dir}gatk_HaplotypeCaller/{{samples}}_{{chromosomes}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Bam : {{input.bam_file}}
                    - Fasta : {{input.reference}}
                    - Chromosome : {{params.interval}}
                Output:
                    - gvcf : {{output.vcf_file}}
                Others
                    - java mem : {{params.java_mem}}
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["GATK4"]
    shell:
         """
            gatk HaplotypeCaller --java-options "-Xmx{params.java_mem}" -R {input.reference} -I {input.bam_file} -O {output.vcf_file} \
            {params.other_options} \
            --native-pair-hmm-threads {threads} \
            -L {params.interval} 1>{log.output} 2>{log.error}
         """


def get_gvcf_list(list):
    gvcf_list = " -V ".join(list)
    return f"-V {gvcf_list}"


rule gatk_GenomicsDBImport:
    """apply GenomicsDBImport on all gvcf by chromosomes """
    threads: get_threads('gatk_GenomicsDBImport', 1)
    input: 	gvcf_list = expand(rules.gatk_HaplotypeCaller.output.vcf_file, samples = rattlesnp.samples , chromosomes = "{chromosomes}"),
            reference = reference_file,
            dict = rules.create_sequence_dict.output.dict
    output:
            db = directory(f"{out_dir}2_snp_calling/GATK_GenomicsDBImport/DB_{{chromosomes}}")
    params:
            java_mem="20g",                   # TODO add argument to cluster_config
            interval = "{chromosomes}",
            str_join = get_gvcf_list(expand(rules.gatk_HaplotypeCaller.output.vcf_file, samples = rattlesnp.samples , chromosomes = "{chromosomes}")),
            other_options = config["PARAMS_TOOLS"]["GATK_GENOMICSDBIMPORT"]
    log:
            error =  f'{log_dir}gatk_GenomicsDBImport/{{chromosomes}}.e',
            output = f'{log_dir}gatk_GenomicsDBImport/{{chromosomes}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - Bam : {{params.str_join}}
                    - Fasta : {{input.reference}}
                    - Chromosome : {{params.interval}}
                Output:
                    - db : {{output.db}}
                Others
                    - java mem : {{params.java_mem}}
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["GATK4"]
    shell:
         """
            gatk GenomicsDBImport --java-options "-Xmx{params.java_mem}" -R {input.reference} {params.str_join} \
            --genomicsdb-workspace-path {output.db} \
            {params.other_options} \
            -L {params.interval} 1>{log.output} 2>{log.error}
         """

rule gatk_GenotypeGVCFs_merge:
    """apply GenotypeGVCFs on all gvcf"""
    threads: get_threads('gatk_GenotypeGVCFs_merge', 1)
    input:
            db = rules.gatk_GenomicsDBImport.output.db,
            reference = reference_file,
            dict = rules.create_sequence_dict.output.dict
    output:
            vcf_file = f'{out_dir}2_snp_calling/SplitByChromosome/All_samples_{{chromosomes}}_GenotypeGVCFs.vcf'
    params:
            java_mem="30g",              # TODO add argument to cluster_config
            other_options = config["PARAMS_TOOLS"]["GATK_GENOTYPEGVCFS"]
    log:
            error =  f'{log_dir}gatk_GenotypeGVCFs_merge/{{chromosomes}}.e',
            output = f'{log_dir}gatk_GenotypeGVCFs_merge/{{chromosomes}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - db : {{input.db}}
                    - Fasta : {{input.reference}}
                Output:
                    - vcf : {{output.vcf_file}}
                Others
                    - java mem : {{params.java_mem}}
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["GATK4"]
    shell:
        """
            gatk GenotypeGVCFs --java-options "-Xmx{params.java_mem}" -R {input.reference} -V gendb://{input.db} -O {output.vcf_file} {params.other_options} 1>{log.output} 2>{log.error}
        """

rule bcftools_concat:
    threads: get_threads('bcftools_concat', 1)
    input:
            vcf_file_all = expand(rules.gatk_GenotypeGVCFs_merge.output.vcf_file, chromosomes = rattlesnp.CHROMOSOMES),
            vcf_file = expand(rules.gatk_GenotypeGVCFs_merge.output.vcf_file, chromosomes = rattlesnp.CHROMOSOMES_WITHOUT_MITO)
    output:
            vcf_file = f'{out_dir}2_snp_calling/All_samples_GenotypeGVCFs_WITHOUT_MITO_raw.vcf.gz',
            tbi_file = f'{out_dir}2_snp_calling/All_samples_GenotypeGVCFs_WITHOUT_MITO_raw.vcf.gz.tbi'
    log:
            error =  f'{log_dir}bcftools_concat/bcftools_concat.e',
            output = f'{log_dir}bcftools_concat/bcftools_concat.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - vcf : {{input.vcf_file}}
                Output:
                    - vcf : {{output.vcf_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["BCFTOOLS"]
    shell:
        """
            bcftools concat --threads {threads} {input.vcf_file} -o {output.vcf_file} -O z 1>{log.output} 2>{log.error}
            bcftools index --threads {threads} --tbi {output.vcf_file} 1>>{log.output} 2>>{log.error}
        """

######################################
# POST VCF
######################################
def get_filter_options(wildcards):
    keys = config["PARAMS"]["FILTER_SUFFIX"]
    values = config["PARAMS_TOOLS"]["VCFTOOLS"]
    dict_options = dict(zip(keys, values))
    options = dict_options[wildcards.vcf_suffix]
    return options


rule vcftools_filter:
    threads: get_threads('vcftools_filter', 1)
    input:
            vcf_file_all = rules.bcftools_concat.output.vcf_file if not rattlesnp.vcf_path else rattlesnp.vcf_path
    output:
            vcf_file = f'{out_dir}4_snp_calling_filter/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.vcf.gz' if f"{{vcf_suffix}}" != "_user" else ""
    params:
            other_options = get_filter_options
    log:
            error =  f'{log_dir}vcftools_filter/vcftools_filter{{vcf_suffix}}.e',
            output = f'{log_dir}vcftools_filter/vcftools_filter{{vcf_suffix}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - vcf : {{input.vcf_file_all}}
                Output:
                    - vcf : {{output.vcf_file}}
                Params:
                    - {{params.other_options}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["VCFTOOLS"],
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
        """
            vcftools --gzvcf {input.vcf_file_all} {params.other_options} --stdout  | sed -r "s#\.\/\.#.#g" | bgzip -c 1> {output.vcf_file}
        """


rule vcf_to_fasta:
    threads: get_threads('vcf_to_fasta', 1)
    input:
            vcf_file_filter = rules.vcftools_filter.output.vcf_file
    output:
            fasta = f'{out_dir}5_fasta_file/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.fasta'
    params:
            fasta = f'{out_dir}4_snp_calling_filter/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.fasta'
    log:
            error =  f'{log_dir}vcf_to_fasta/vcf_to_fasta{{vcf_suffix}}.e',
            output = f'{log_dir}vcf_to_fasta/vcf_to_fasta{{vcf_suffix}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - vcf : {{input.vcf_file_filter}}
                Output:
                    - fasta : {{output.fasta}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["PYTHON3"]
    shell:
        f"""
        vcf2phylip -i {{input.vcf_file_filter}} -p -f
        mv {{params.fasta}} {{output.fasta}}
        """

rule vcf_to_geno:
    threads: get_threads('vcf_to_geno', 1)
    input:
            vcf_file_filter = rules.vcftools_filter.output.vcf_file
    output:
            geno = f'{out_dir}7_geno_file/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.geno'
    log:
            error =  f'{log_dir}vcf_to_geno/vcf_to_geno{{vcf_suffix}}.e',
            output = f'{log_dir}vcf_to_geno/vcf_to_geno{{vcf_suffix}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - vcf : {{input.vcf_file_filter}}
                Output:
                    - geno : {{output.geno}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["PYTHON3"]
    shell:
        f"""
        vcf2geno --vcf {{input.vcf_file_filter}} --geno {{output.geno}}
        """

######################################
# VCF STATS
######################################
def vcf_to_stats(wildcards):
    if rattlesnp.vcf_path and wildcards.vcf_suffix == "_user":
        return rattlesnp.vcf_path
    elif wildcards.vcf_suffix == "_raw":
        return rules.bcftools_concat.output.vcf_file
    elif wildcards.vcf_suffix in config['PARAMS']['FILTER_SUFFIX']:
        return rules.vcftools_filter.output.vcf_file

rule vcf_stats:
    threads: get_threads('vcf_stats', 1)
    input:
            vcf_file_all = vcf_to_stats
    output:
            freq = f'{out_dir}3_all_snp_calling_stats/All_samples_GenotypeGVCFs{{vcf_suffix}}.frq',
            depth = f'{out_dir}3_all_snp_calling_stats/All_samples_GenotypeGVCFs{{vcf_suffix}}.idepth',
            depth_mean = f'{out_dir}3_all_snp_calling_stats/All_samples_GenotypeGVCFs{{vcf_suffix}}.ldepth.mean',
            qual = f'{out_dir}3_all_snp_calling_stats/All_samples_GenotypeGVCFs{{vcf_suffix}}.lqual',
            missing_ind = f'{out_dir}3_all_snp_calling_stats/All_samples_GenotypeGVCFs{{vcf_suffix}}.imiss',
            miss = f'{out_dir}3_all_snp_calling_stats/All_samples_GenotypeGVCFs{{vcf_suffix}}.lmiss'
    params:
            dirout = directory(f'{out_dir}3_all_snp_calling_stats/')
    log:
            error =  f'{log_dir}vcf_stats/vcftools{{vcf_suffix}}.e',
            output = f'{log_dir}vcf_stats/vcftools{{vcf_suffix}}.o'
    message:
            f"""
            Execute {{rule}} for
                Input:
                    - vcf : {{input.vcf_file_all}}
                Output:
                    - freq : {{output.freq}}
                    - depth : {{output.depth}}
                    - depth_mean : {{output.depth_mean}}
                    - qual : {{output.qual}}
                    - missing_ind : {{output.missing_ind}}
                    - miss : {{output.miss}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["VCFTOOLS"],
        tools_config["MODULES"]["SAMTOOLS"]
    shell:
        """
            (vcftools --gzvcf {input.vcf_file_all}  --remove-indels --freq2 --max-alleles 3 --stdout 1> {output.freq}
            vcftools --gzvcf {input.vcf_file_all}  --remove-indels --depth --stdout 1> {output.depth}
            vcftools --gzvcf {input.vcf_file_all}  --remove-indels --site-mean-depth --stdout 1> {output.depth_mean}
            vcftools --gzvcf {input.vcf_file_all}  --remove-indels --site-quality --stdout 1> {output.qual}
            vcftools --gzvcf {input.vcf_file_all}  --remove-indels --missing-indv --stdout 1> {output.missing_ind}
            vcftools --gzvcf {input.vcf_file_all}  --remove-indels --missing-site --stdout 1> {output.miss}) 2>>{log.error}
        """

rule report_vcf:
    threads: get_threads('report_vcf', 1)
    input:
            freq = rules.vcf_stats.output.freq,
            depth = rules.vcf_stats.output.depth,
            depth_mean = rules.vcf_stats.output.depth_mean,
            qual = rules.vcf_stats.output.qual,
            missing_ind = rules.vcf_stats.output.missing_ind,
            miss = rules.vcf_stats.output.miss
    output:
            report = f"{out_dir}3_all_snp_calling_stats/report_vcf{{vcf_suffix}}.html"
    log:
            error =  f'{log_dir}report_vcf/report{{vcf_suffix}}.e',
            output = f'{log_dir}report_vcf/report{{vcf_suffix}}.o'
    # envmodules:
        # tools_config["MODULES"]["R"]
    message:
            f"""
            Execute {{rule}} for
                Input:
                    - freq : {{input.freq}}
                    - depth : {{input.depth}}
                    - depth_mean : {{input.depth_mean}}
                    - qual : {{input.qual}}
                    - missing_ind : {{input.missing_ind}}
                    - miss : {{input.miss}}
                Output:
                    - report : {{output.report}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    script:
        """script/report_vcf.Rmd"""
######################################
# Genetic tools like RaxML, SNMF, ...
######################################
rule run_raxml:
    """run raxml"""
    threads: get_threads('run_raxml', 1)
    input:
            fasta = rules.vcf_to_fasta.output.fasta
    output:
            tree = f'{out_dir}6_raxml/filter{{vcf_suffix}}/RAxML_bestTree.All_samples_GenotypeGVCFs_filter{{vcf_suffix}}',
            dir = directory(f'{out_dir}6_raxml/filter{{vcf_suffix}}/')
    params:
            other_params = config["PARAMS_TOOLS"]["RAXML"]
    log:
            error =  f'{log_dir}raxml/raxml{{vcf_suffix}}.e',
            output = f'{log_dir}raxml/raxml{{vcf_suffix}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - fasta : {{input.fasta}}
                Output:
                    - tree : {{output.tree}}
                    - dir : {{output.dir}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["RAXML"]
    shell:
        """
            raxmlHPC-PTHREADS -T {threads} -s {input.fasta} -w {output.dir} -n {params.other_params}
        """


rule run_raxml_ng:
    """run raxml"""
    threads: get_threads('run_raxml_ng', 1)
    input:
            fasta = rules.vcf_to_fasta.output.fasta
    output:
            tree = f'{out_dir}6_raxml_ng/filter{{vcf_suffix}}/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}.raxml.bestTree',
            dir = directory(f'{out_dir}6_raxml_ng/filter{{vcf_suffix}}/')
    params:
            prefix = f'{out_dir}6_raxml_ng/filter{{vcf_suffix}}/All_samples_GenotypeGVCFs_filter{{vcf_suffix}}',
            other_params = lambda wildcards: config["PARAMS_TOOLS"]["RAXML_NG"]
    log:
            error =  f'{log_dir}raxml_ng/raxml{{vcf_suffix}}.e',
            output = f'{log_dir}raxml_ng/raxml{{vcf_suffix}}.o'
    message:
            f"""
            Running {{rule}}
                Input:
                    - fasta : {{input.fasta}}
                Output:
                    - tree : {{output.tree}}
                    - dir : {{output.dir}}
                Params:
                    - other: {{params.other_params}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            """
    envmodules:
        tools_config["MODULES"]["RAXML_NG"]
    shell:
        """
            raxml-ng --threads {threads} --msa {input.fasta} --prefix {params.prefix} {params.other_params}
        """
