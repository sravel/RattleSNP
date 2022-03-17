from pathlib import Path
from collections import defaultdict, OrderedDict


def parse_idxstats(files_list=None, out_csv=None, sep="\t"):
    from pathlib import Path
    from collections import defaultdict, OrderedDict
    import pandas as pd
    dico_mapping_stats = defaultdict(OrderedDict)
    for csv_file in files_list:
        sample = Path(csv_file).stem.split("_")[0]
        df = pd.read_csv(csv_file, sep="\t", header=None,names=["chr","chr_size","map_paired","map_single"], index_col=False)
        # print(df)
        unmap = df[df.chr == '*'].map_single.values[0]
        df = df[df.chr != '*']
        map_total = df["map_single"].sum()+df["map_paired"].sum()
        size_lib = map_total+unmap
        percent = map_total/size_lib
        dico_mapping_stats[f"{sample}"]["size_lib"] = size_lib
        dico_mapping_stats[f"{sample}"]["map_total"] = map_total
        dico_mapping_stats[f"{sample}"]["percent"] = f"{percent*100:.2f}%"
    dataframe_mapping_stats = pd.DataFrame.from_dict(dico_mapping_stats, orient='index')
    with open(out_csv, "w") as out_csv_file:
        # print(f"Library size:\n{dataframe_mapping_stats}\n")
        dataframe_mapping_stats.to_csv(out_csv_file, index=True, sep=sep)


def check_mapping_stats(bam, depth_file, out_csv, sep="\t"):
    from numpy import median, mean
    import pysam
    import re
    import pandas as pd
    dico_size_ref_genome = {}
    dicoResume = defaultdict(OrderedDict)
    # for bam in bam_files:
    if not Path(bam+"bai").exists(): pysam.index(Path(bam).as_posix())
    sample = Path(bam).stem
    listMap = []
    with open(depth_file, "r") as depth_file_open:
        for line in depth_file_open:
            depth = line.rstrip().split("\t")[-1]
            listMap.append(int(depth))
    bam_file = pysam.AlignmentFile(bam, "r")
    name_fasta_ref = Path(re.findall("[/].*\.fasta",bam_file.header["PG"][0]["CL"], flags=re.IGNORECASE)[0]).stem
    if name_fasta_ref not in dico_size_ref_genome:
        dico_size_ref_genome[name_fasta_ref] = sum([dico["LN"] for dico in bam_file.header["SQ"]])
    dicoResume[sample]["Mean Depth"] = f"{mean(listMap):.2f}X"
    dicoResume[sample]["Median Depth"] = f"{median(listMap):.2f}X"
    dicoResume[sample]["Max Depth"] = f"{max(listMap):.2f}X"
    dicoResume[sample]["Mean Genome coverage"] = f"{(len(listMap)/dico_size_ref_genome[name_fasta_ref])*100:.2f}%"

    dataframe_mapping_stats = pd.DataFrame.from_dict(dicoResume, orient='index')
    with open(out_csv, "w") as out_csv_file:
        # print(f"Library size:\n{dataframe_mapping_stats}\n")
        dataframe_mapping_stats.to_csv(out_csv_file, index=True, sep=sep)


def merge_bam_stats_csv(csv_files, csv_file, sep="\t"):
    # dir = Path(csv_files)
    import pandas as pd
    df = (pd.read_csv(f, sep=sep) for f in csv_files)
    df = pd.concat(df)
    df.rename(columns={'Unnamed: 0':'Samples'}, inplace=True)
    with open(csv_file, "w") as libsizeFile:
        # print(f"All CSV infos:\n{df}\n")
        df.to_csv(libsizeFile, index=False, sep=sep)


def tsv_per_chromosome(gvcf_files, tsv_file, sep="\t"):
    import pandas as pd
    from pathlib import Path
    dico = {(Path(file).stem.split('-')[0], file) for file in gvcf_files}
    df = pd.DataFrame.from_dict(dico)
    with open(tsv_file, "w") as out_tsv_file:
        # print(f"Library size:\n{dataframe_mapping_stats}\n")
        df.to_csv(out_tsv_file, index=False, header=False, sep=sep)
