## Snakemake - Mapping_pipeline
##
## @RAVEL-Sebastien
##

import pprint
from pathlib import Path

from script.module import parse_idxstats, check_mapping_stats, merge_bam_stats_csv

pp = pprint.PrettyPrinter(indent=4)

###############################################################################
# NOTE pas de caractere speciaux entre 2 wildcards

# --- Importing Configuration Files --- #
configfile: 'config.yaml'
cluster_config: "cluster_config.yaml"

# pp.pprint(cluster_config["gatk_HaplotypeCaller"]["javaMem"])
# pp.pprint(cluster_config)
# exit()

# dir and suffix
samples_dir = config["DATA"]["directories"]["samples_dir"]
reference_file =  config["DATA"]["directories"]["reference_file"]
basename_reference = Path(reference_file).stem
cleanning =  config["cleanning"]
build_stats =  config["build_stats"]

# print(basename_reference)
out_dir = config["DATA"]["directories"]["out_dir"]
log_dir = f"{out_dir}LOGS/"
# to lunch separator
sep="#"

#############################################
# use threads define in cluster_config rule or rule default or default in snakefile
#############################################
def get_threads(rule, default):
    """
    use threads define in cluster_config rule or rule default or default in snakefile
    :param rule:
    :param default:
    :return: int(threads)
    """
    if rule in cluster_config and 'threads' in cluster_config[rule]:
        return int(cluster_config[rule]['threads'])
    elif '__default__' in cluster_config and 'threads' in cluster_config['__default__']:
        return int(cluster_config['__default__']['threads'])
    return default

#*###############################################################################
def get_list_chromosome_names(fasta_file):
    """
            Return the list of sequence name on the fasta file.
            Work with Biopython and python version >= 3.5
    """
    from Bio import SeqIO
    return [*SeqIO.to_dict(SeqIO.parse(fasta_file,"fasta"))]

#*###############################################################################
def build_log_path(debug = False):
    """
        Create '{working_dir}LOGS/{rules_name}' to prepare log path for all rules.
        The function is need when you run on cluster mode but is mandatory to append the call at the end of Snakefile like
        build_log_path(debug=False)
        Debug option is to print only the path.
    :param debug:
    :return:
    """
    if debug:
        print("\n".join(Path(f"{log_dir}{rule.name}/").as_posix() for rule in list(workflow.rules)))
    else:
        [Path(f"{log_dir}{rule.name}/").mkdir(parents=True, exist_ok=True) for rule in list(workflow.rules)]

#*###############################################################################
def get_files_path(wildcards):
    """


    :param wildcards:
    :return: dict
    """
    if Path(f"{samples_dir}{wildcards.samples}_R2.fastq.gz").exists():
        return {"bam_in" : rules.bwa_sampe_sort_bam.output.bam_file,
                "R1": rules.bwa_sampe_sort_bam.input.R1,
                "R2": rules.bwa_sampe_sort_bam.input.R2
                }
    else:
        return {"bam_in" : rules.bwa_samse_sort_bam.output.bam_file,
                "R1": rules.bwa_samse_sort_bam.input.R1
                }
#*###############################################################################
SAMPLES, = glob_wildcards(samples_dir+"{samples}_R1.fastq.gz", followlinks=True)
CHROMOSOMES = get_list_chromosome_names(reference_file)
CHROMOSOMES_WITHOUT_MITO = CHROMOSOMES.copy()
CHROMOSOMES_WITHOUT_MITO.remove(config["DATA"]['mitochondrial_name'])

# Auto check if data is paired with flag _R2
SAMPLES_PAIRED = []
SAMPLES_SINGLE = []
for sample in SAMPLES:
    if Path(f"{samples_dir}{sample}_R2.fastq.gz").exists():
        SAMPLES_PAIRED.append(sample)
    else:
        SAMPLES_SINGLE.append(sample)

# print(f"SAMPLES_SINGLE: {SAMPLES_SINGLE}")
# print(f"SAMPLES_PAIRED: {SAMPLES_PAIRED}")
# exit()


def output_final(wildcars):
    """
    FINAL RULE
    :param wildcars:
    :return:
    """
    dico_final = {
                    "vcf" : f'{out_dir}5_snp_calling_final/All_samples_GenotypeGVCFs.vcf.gz'
                }
    if cleanning:
        dico_final.update({
                    "fastQC_files_PE" : expand(f"{out_dir}0_cleanning/paired/{{samples}}_R2.ATROPOS_fastqc.html", samples = SAMPLES_PAIRED),
                    "fastQC_files_SE" : expand(f"{out_dir}0_cleanning/single/{{samples}}_R1.ATROPOS_fastqc.html", samples = SAMPLES_SINGLE),
                })
    if build_stats:
        dico_final.update({
                    "depth_resume" : f"{out_dir}2_mapping_stats/resume/all_mapping_stats_Depth_resume.csv",
                    "idxstats_resume" : f"{out_dir}2_mapping_stats/resume/all_mapping_stats_resume.csv",
                })
    # print(dico_final)
    return dico_final


# --- Main Build Rules --- #
rule final:
    """construct a table of all resume files"""
    input:
        unpack(output_final)


# 0 index of genome file
rule bwa_index:
    """make index with bwa for reference file"""
    threads: get_threads('bwa_index', 1)
    input:
            fasta = reference_file
    output:
            sa_file = reference_file+".sa"
    log :
            error =  f'{log_dir}bwa_index/{basename_reference}.e',
            output = f'{log_dir}bwa_index/{basename_reference}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fasta : {{input.fasta}}
                Output:
                    - sa_file: {{output.sa_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["BWA"]+"""
                bwa index {input.fasta} 1>{log.output} 2>{log.error}
            """

# 1=atropos PE
rule run_atropos_PE:
    """Run atropos for cleanning data"""
    threads: get_threads('run_atropos_PE', 1)
    input:
            R1 = f"{samples_dir}{{samples}}_R1.fastq.gz",
            R2 = f"{samples_dir}{{samples}}_R2.fastq.gz",
    output:
            R1 = f"{out_dir}0_cleanning/paired/{{samples}}_R1.ATROPOS.fastq.gz",
            R2 = f"{out_dir}0_cleanning/paired/{{samples}}_R2.ATROPOS.fastq.gz"
    log :
            error =  f'{log_dir}run_atropos_PE/{{samples}}.e',
            output = f'{log_dir}run_atropos_PE/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
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
            {sep*108}"""
    shell: config["MODULES"]["ATROPOS"]+"""
        atropos --threads {threads} """+config["PARAMSTOOLS"]["ATROPOSPE"]+""" -o {output.R1} -p {output.R2} -pe1 {input.R1} -pe2 {input.R2}  1>{log.output} 2>{log.error}
    """

# 1=atropos
rule run_atropos_SE:
    """Run atropos for cleanning data"""
    threads: get_threads('run_atropos_SE', 1)
    input:
            R1 = f"{samples_dir}{{samples}}_R1.fastq.gz",
    output:
            R1 = f"{out_dir}0_cleanning/single/{{samples}}_R1.ATROPOS.fastq.gz",
    log :
            error =  f'{log_dir}run_atropos_SE/{{samples}}.e',
            output = f'{log_dir}run_atropos_SE/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fastq R1 : {{input.R1}}
                Output:
                    - Fastq R1 : {{output.R1}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["ATROPOS"]+"""
                atropos --threads {threads} """+config["PARAMSTOOLS"]["ATROPOSSE"]+""" -o {output.R1} -se {input.R1}  1>{log.output} 2>{log.error}
            """

# 2=fastqc
rule run_fastqc_PE:
    """Run fastqc for controle data"""
    threads: get_threads('run_fastqc_PE', 1)
    input:
            R1 = rules.run_atropos_PE.output.R1,
            R2 = rules.run_atropos_PE.output.R2
    output:
            R1 = f"{out_dir}0_cleanning/paired/{{samples}}_R1.ATROPOS_fastqc.html",
            R2 = f"{out_dir}0_cleanning/paired/{{samples}}_R2.ATROPOS_fastqc.html"
    log :
            error =  f'{log_dir}run_fastqc_PE/{{samples}}.e',
            output = f'{log_dir}run_fastqc_PE/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
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
            {sep*108}"""
    shell:
            config["MODULES"]["FASTQC"]+"""
                fastqc -t {threads} {input.R1} {input.R2}  1>{log.output} 2>{log.error}
            """

rule run_fastqc_SE:
    """Run fastqc for controle data"""
    threads: get_threads('run_fastqc_SE', 1)
    input:
            R1 = rules.run_atropos_SE.output.R1
    output:
            R1 = f"{out_dir}0_cleanning/single/{{samples}}_R1.ATROPOS_fastqc.html",
    log :
            error =  f'{log_dir}run_fastqc_SE/{{samples}}.e',
            output = f'{log_dir}run_fastqc_SE/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fastq R1 : {{input.R1}}
                Output:
                    - html R1 : {{output.R1}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell: config["MODULES"]["FASTQC"]+"""
        fastqc -t {threads} {input.R1}  1>{log.output} 2>{log.error}
    """

# 3=bwaAln
rule run_bwa_aln_PE:
    """make bwa aln for all samples PE on reference"""
    threads: get_threads('run_bwa_aln_PE', 1)
    input:
            fasta = reference_file,
            index = rules.bwa_index.output.sa_file,
            R1 = f"{samples_dir}{{samples}}_R1.fastq.gz" if not cleanning else rules.run_atropos_PE.output.R1 ,
            R2 = f"{samples_dir}{{samples}}_R2.fastq.gz" if not cleanning else rules.run_atropos_PE.output.R2
    output:
            sai_R1 = temp(f"{out_dir}1_mapping/paired/{{samples}}_R1.BWAALN.sai"),
            sai_R2 = temp(f"{out_dir}1_mapping/paired/{{samples}}_R2.BWAALN.sai")
    log:
            error =  f'{log_dir}run_bwa_aln_PE/{{samples}}.e',
            output = f'{log_dir}run_bwa_aln_PE/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
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
            {sep*108}"""
    shell:
            config["MODULES"]["BWA"]+"""
                bwa aln -t {threads} -f {output.sai_R1} {input.fasta} {input.R1} 1>{log.output} 2>{log.error} &&
                bwa aln -t {threads} -f {output.sai_R2} {input.fasta} {input.R2} 1>{log.output} 2>{log.error}
            """

rule run_bwa_aln_SE:
    """make bwa aln for all samples SE on reference"""
    threads: get_threads('run_bwa_aln_SE', 1)
    input: 	fasta = reference_file,
            index = rules.bwa_index.output.sa_file,
            R1 = f"{samples_dir}{{samples}}_R1.fastq.gz" if not cleanning else rules.run_atropos_SE.output.R1
    output:
            sai_R1 = temp(f"{out_dir}1_mapping/single/{{samples}}_R1.BWAALN.sai"),
    log:
            error =  f'{log_dir}run_bwa_aln_SE/{{samples}}.e',
            output = f'{log_dir}run_bwa_aln_SE/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fasta : {{input.fasta}}
                    - R1: {{input.R1}}
                Output:
                    - sai R1: temp({{output.sai_R1}})
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["BWA"]+"""
                bwa aln -t {threads} -f {output.sai_R1} {input.fasta} {input.R1} 1>{log.output} 2>{log.error}
            """

rule bwa_samse_sort_bam:
    """make bwa samse for all samples SE on reference"""
    threads: get_threads('bwa_samse_sort_bam', 1)
    input: 	fasta = reference_file,
            index = rules.bwa_index.output.sa_file,
            R1 = rules.run_bwa_aln_SE.input.R1,
            sai_R1 = rules.run_bwa_aln_SE.output.sai_R1
    output:
            bam_file = f"{out_dir}1_mapping/single/{{samples}}.bam"
    params:
            rg = f"@RG\\tID:{{samples}}\\tSM:{{samples}}\\tPL:Illumina"
    log:
            error =  f'{log_dir}bwa_samse_sort_bam/{{samples}}.e',
            output = f'{log_dir}bwa_samse_sort_bam/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fasta : {{input.fasta}}
                    - R1: {{input.R1}} 
                Output:
                    - Bam: {{output.bam_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["BWA"]+"\n"+config["MODULES"]["SAMTOOLS"]+"""
                bwa samse -r"{params.rg}"{input.fasta} {input.sai_R1} {input.R1} 2>{log.error} |
                samtools view -@ {threads} -bh 2>{log.error} |
                samtools sort -@ {threads} -o {output.bam_file} 1>{log.output} 2>{log.error}
            """

rule bwa_sampe_sort_bam:
    """make bwa sampe for all samples PE on reference"""
    threads: get_threads('bwa_sampe_sort_bam', 1)
    input:
            fasta = reference_file,
            index = rules.bwa_index.output.sa_file,
            R1 = rules.run_bwa_aln_PE.input.R1,
            R2 = rules.run_bwa_aln_PE.input.R2,
            sai_R1 = rules.run_bwa_aln_PE.output.sai_R1,
            sai_R2 = rules.run_bwa_aln_PE.output.sai_R2
    output:
            bam_file = out_dir+'1_mapping/paired/{samples}.bam'
    params:
            rg = f"@RG\\tID:{{samples}}\\tSM:{{samples}}\\tPL:Illumina"
    log:
            error =  f'{log_dir}bwa_sampe_sort_bam/{{samples}}.e',
            output = f'{log_dir}bwa_sampe_sort_bam/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fasta : {{input.fasta}}
                    - R1: {{input.R1}}
                    - R2: {{input.R2}}
                Output:
                    - Bam: {{output.bam_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["BWA"]+"\n"+config["MODULES"]["SAMTOOLS"]+"""
                bwa sampe -r"{params.rg}" {input.fasta} {input.sai_R1} {input.sai_R2} {input.R1} {input.R2} 2>{log.error} |
                samtools view -@ {threads} -bh 2>{log.error} |
                samtools sort -@ {threads} -o {output.bam_file} 1>{log.output} 2>{log.error}
            """

rule merge_bam_directories:
    """Merge paired and single on same directory and index"""
    threads: get_threads('merge_bam_directories', 1)
    input:
            unpack(get_files_path)
    output:
            bam_all = f"{out_dir}1_mapping/all/{{samples}}.bam",
            bai = f"{out_dir}1_mapping/all/{{samples}}.bam.bai"
    log:
            error =  f'{log_dir}merge_bam_directories/{{samples}}.e',
            output = f'{log_dir}merge_bam_directories/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Bam : {{input.bam_in}}
                Output:
                    - Bam : {{output.bam_all}}
                    - Bai : {{output.bai}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["SAMTOOLS"]+"""
                ln -s {input.bam_in} {output.bam_all} 1>{log.output} 2>{log.error}
                samtools index {output.bam_all} 1>>{log.output} 2>>{log.error}
            """
####### Stats
rule samtools_idxstats:
    """apply samtools idxstats on all bam SE end PE"""
    threads: get_threads('samtools_idxstats', 1)
    input:
            bam = rules.merge_bam_directories.output.bam_all
    output:
            txt_file = f"{out_dir}2_mapping_stats/all/{{samples}}_IDXSTATS.txt"
    log:
            error =  f'{log_dir}samtools_idxstats/{{samples}}.e',
            output = f'{log_dir}samtools_idxstats/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Bam : {{input.bam}}
                Output:
                    - txt : {{output.txt_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["SAMTOOLS"]+"""
                samtools idxstats -@ {threads} {input.bam} | tee {output.txt_file} 1>{log.output} 2>{log.error}
            """
rule merge_idxstats:
    """merge all samtools idxstats files"""
    threads : get_threads('merge_idxstats', 1)
    input :
            csv_resume = expand(rules.samtools_idxstats.output.txt_file , samples = SAMPLES),
    output :
            csv_resume_merge = report(f"{out_dir}2_mapping_stats/resume/all_mapping_stats_resume.csv", category="Resume mapping infos")
    log:
            error =  f'{log_dir}merge_idxstats/all_mapping_stats_resume.e',
            output = f'{log_dir}merge_idxstats/all_mapping_stats_resume.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - CSV_files : {{input.csv_resume}}
                Output:
                    - Merge CSV : {{output.csv_resume_merge}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    run :
        parse_idxstats(input.csv_resume, output.csv_resume_merge, sep="\t")

########################## STATS BAM
rule samtools_depth:
    """apply samtools depth on all bam SE end PE"""
    threads: get_threads('samtools_depth', 1)
    input:
            bam = rules.merge_bam_directories.output.bam_all
    output:
            txt_file = f"{out_dir}2_mapping_stats/all/{{samples}}_DEPTH.txt"
    log:
            error =  f'{log_dir}samtools_depth/{{samples}}.e',
            output = f'{log_dir}samtools_depth/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Bam : {{input.bam}}
                Output:
                    - txt : {{output.txt_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
            config["MODULES"]["SAMTOOLS"]+"""
                samtools depth {input.bam} | tee {output.txt_file} 1>{log.output} 2>{log.error}
            """

rule bam_stats_to_csv:
    """build csv with mean depth, median depth and mean coverage for all bam"""
    threads : get_threads('bam_stats_to_csv', 1)
    input :
            bam_file = rules.merge_bam_directories.output.bam_all
    output :
            csv_resume = temp(f'{out_dir}2_mapping_stats/all/{{samples}}_Depth_resume.csv')
    log:
            error =  f'{log_dir}bam_stats_to_csv/{{samples}}.e',
            output = f'{log_dir}bam_stats_to_csv/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Bam : {{input.bam_file}}
                Output:
                    - CSV : temp({{output.csv_resume}})
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    run :
        check_mapping_stats(input.bam_file, output.csv_resume, sep="\t")

rule merge_bam_stats:
    """merge all bam_stats_to_csv files"""
    threads : get_threads('merge_bam_stats', 1)
    input :
            csv_resume = expand(rules.bam_stats_to_csv.output.csv_resume , samples = SAMPLES),
    output :
            csv_resume_merge = report(f"{out_dir}2_mapping_stats/resume/all_mapping_stats_Depth_resume.csv", category="Resume mapping infos")
    log:
            error =  f'{log_dir}merge_bam_stats/mergeResume.e',
            output = f'{log_dir}merge_bam_stats/mergeResume.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - CSV list : {{input.csv_resume}}
                Output:
                    - CSV : temp({{output.csv_resume_merge}})
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    run :
        merge_bam_stats_csv(input.csv_resume, output.csv_resume_merge, sep="\t")

########################## Mapping améliorations
# 11=picardToolsMarkDuplicates

rule picardTools_mark_duplicates:
    """apply gatk_realigner_target_creator on all bam SE end PE"""
    threads: get_threads('picardTools_mark_duplicates', 1)
    input:
            bam_file = rules.merge_bam_directories.output.bam_all
    output:
            bam_file = f"{out_dir}1_mapping/all/{{samples}}_picardTools-mark-duplicates.bam",
            txt_file = f"{out_dir}1_mapping/all/{{samples}}_picardTools-mark-duplicates.metrics"
    log:
            error =  f'{log_dir}picardTools_mark_duplicates/{{samples}}.e',
            output = f'{log_dir}picardTools_mark_duplicates/{{samples}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Bam : {{input.bam_file}}
                Output:
                    - Bam : {{output.bam_file}}
                    - metric : {{output.txt_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell: config["MODULES"]["PICARDTOOLS"]+"""
        java -jar $PICARDPATH/picard.jar MarkDuplicates CREATE_INDEX=TRUE VALIDATION_STRINGENCY=SILENT INPUT={input.bam_file} OUTPUT={output.bam_file} METRICS_FILE={output.txt_file} 1>{log.output} 2>{log.error}
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
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - Fasta : {{input.reference}}
                Output:
                    - dict : {{output.dict}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell: config["MODULES"]["GATK4"]+"""
    gatk CreateSequenceDictionary --java-options "-Xmx{params.java_mem}" -R {input.reference} 1>{log.output} 2>{log.error}
    """

rule gatk_HaplotypeCaller:
    """apply gatk_HaplotypeCaller on all bam SE end PE"""
    threads: get_threads('gatk_HaplotypeCaller', 1)
    input:
            bam_file = rules.picardTools_mark_duplicates.output.bam_file,
            reference = reference_file,
            dict = rules.create_sequence_dict.output.dict,
    output:
            vcf_file = f"{out_dir}3_snp_calling/{{samples}}-{{chromosomes}}_GATK4.gvcf"
    params:
            java_mem="4g",                  # TODO add argument to cluster_config
            interval = "{chromosomes}"
    log:
            error =  f'{log_dir}gatk_HaplotypeCaller/{{samples}}_{{chromosomes}}.e',
            output = f'{log_dir}gatk_HaplotypeCaller/{{samples}}_{{chromosomes}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
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
            {sep*108}"""
    shell: config["MODULES"]["GATK4"]+"""
    gatk HaplotypeCaller --java-options "-Xmx{params.java_mem}" -R {input.reference} -I {input.bam_file} -O {output.vcf_file} \
    --emit-ref-confidence GVCF \
    --output-mode EMIT_ALL_ACTIVE_SITES \
    --native-pair-hmm-threads {threads} \
    -ploidy 1 \
    -L {params.interval} 1>{log.output} 2>{log.error}
    """


def get_gvcf_list(list):
    gvcf_list = " -V ".join(list)
    return(f"-V {gvcf_list}")


rule gatk_GenomicsDBImport:
    """apply GenomicsDBImport on all gvcf by chromosomes """
    threads: get_threads('gatk_GenomicsDBImport', 1)
    input: 	gvcf_list = expand(rules.gatk_HaplotypeCaller.output.vcf_file, samples = SAMPLES , chromosomes = "{chromosomes}"),
            reference = reference_file,
            dict = rules.create_sequence_dict.output.dict,
    output:
            db = directory(f"{out_dir}4_DB_import/DB_{{chromosomes}}"),
    params:
            java_mem="8g",                   # TODO add argument to cluster_config
            interval = "{chromosomes}",
            str_join = get_gvcf_list(expand(rules.gatk_HaplotypeCaller.output.vcf_file, samples = SAMPLES , chromosomes = "{chromosomes}"))
    log:
            error =  f'{log_dir}gatk_GenomicsDBImport/{{chromosomes}}.e',
            output = f'{log_dir}gatk_GenomicsDBImport/{{chromosomes}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
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
            {sep*108}"""
    shell: config["MODULES"]["GATK4"]+"""
    gatk GenomicsDBImport --java-options "-Xmx{params.java_mem}" -R {input.reference} {params.str_join} \
    --genomicsdb-workspace-path {output.db} \
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
            vcf_file = f'{out_dir}3_snp_calling/All_samples_{{chromosomes}}_GenotypeGVCFs.vcf',
    params:
            java_mem="30g",              # TODO add argument to cluster_config
    log:
            error =  f'{log_dir}gatk_GenotypeGVCFs_merge/{{chromosomes}}.e',
            output = f'{log_dir}gatk_GenotypeGVCFs_merge/{{chromosomes}}.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
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
            {sep*108}"""
    shell:
        config["MODULES"]["GATK4"]+"""
            gatk GenotypeGVCFs --java-options "-Xmx{params.java_mem}" -R {input.reference} -V gendb://{input.db} -O {output.vcf_file} -new-qual 1>{log.output} 2>{log.error}
        """

rule bcftools_concat:
    threads: get_threads('bcftools_concat', 1)
    input:
            vcf_file_all = expand(rules.gatk_GenotypeGVCFs_merge.output.vcf_file, chromosomes = CHROMOSOMES),
            vcf_file = expand(rules.gatk_GenotypeGVCFs_merge.output.vcf_file, chromosomes = CHROMOSOMES_WITHOUT_MITO),
    output:
            vcf_file = f'{out_dir}5_snp_calling_final/All_samples_GenotypeGVCFs.vcf.gz',
    log:
            error =  f'{log_dir}bcftools_concat/bcftools_concat.e',
            output = f'{log_dir}bcftools_concat/bcftools_concat.o'
    message:
            f"""
            {sep*108}
            Execute {{rule}} for 
                Input:
                    - vcf : {{input.vcf_file}}
                Output:
                    - vcf : {{output.vcf_file}}
                Others
                    - Threads : {{threads}}
                    - LOG error: {{log.error}}
                    - LOG output: {{log.output}}
            {sep*108}"""
    shell:
        config["MODULES"]["BCFTOOLS"]+"""
            bcftools concat --threads {threads} {input.vcf_file} -o {output.vcf_file} -O z 1>{log.output} 2>{log.error}
        """
################################################################################
# create log dir path
build_log_path(debug=False)