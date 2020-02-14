#!/bin/bash
#rm snakejob.*
module purge
module load system/python/3.7.3
module load system/graphviz/2.40.1

cluster_config=`pwd`"/cluster_config.yaml"
datas_config=`pwd`"/config.yaml"

# produit le graph du pipeline
#snakemake --configfile ${datas_config} --cluster-config ${cluster_config} --rulegraph  > schema_pipeline_global.dot && dot schema_pipeline_global.dot -Tpdf > schema_pipeline_global.pdf

#snakemake --configfile ${datas_config} --cluster-config ${cluster_config}  --dry-run
#snakemake --configfile ${datas_config} --cluster-config ${cluster_config}  --dag > schema_pipeline_samples.dot && dot schema_pipeline_samples.dot -Tpdf > schema_pipeline_samples.pdf
#exit

snakemake --latency-wait 5184000 --jobs 100 --cluster "qsub {cluster.queue} {cluster.export_env} {cluster.cwd} {cluster.mem} {cluster.n_cpu} {cluster.logerror} {cluster.log} " --cluster-config ${cluster_config}  --configfile ${datas_config}

#snakemake --shadow-prefix ${scratch_dir} --latency-wait 5184000 --jobs 100 --drmaa "{cluster.queue} {cluster.export_env} {cluster.cwd} {cluster.mem} {cluster.n_cpu}{threads} {cluster.logerror}{params.errorLog} {cluster.log}{params.outputLog} " --cluster-config ${cluster_config}  --configfile ${datas_config}


#snakemake --configfile ${datas_config} --cluster-config ${cluster_config}  --filegraph | dot -Tpdf > schema_pipeline_files.pdf
#snakemake --configfile ${datas_config} --cluster-config ${cluster_config}  --dag | dot -Tpdf > schema_pipeline_samples.pdf
snakemake --report REPORT.html

## add to clean files
##snakemake -s sRNA_pipeline.snake clean
