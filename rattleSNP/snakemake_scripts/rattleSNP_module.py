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


def check_mapping_stats(bam, out_csv, sep="\t"):
    from numpy import median, mean
    from pysamstats import load_coverage
    import pysam
    import re
    import pandas as pd
    dico_size_ref_genome = {}
    dicoResume = defaultdict(OrderedDict)
    # for bam in bam_files:
    if not Path(bam+"bai").exists(): pysam.index(Path(bam).as_posix())
    sample = Path(bam).stem
    # print(f"\n\n{'*'*30}\nSAMPLE NAME: {sample}\n{'*'*30}\n\n")
    bam_file = pysam.AlignmentFile(bam, "r")
    name_fasta_ref = Path(re.findall("[/].*\.fasta",bam_file.header["PG"][0]["CL"], flags=re.IGNORECASE)[0]).stem
    if name_fasta_ref not in dico_size_ref_genome:
        dico_size_ref_genome[name_fasta_ref] = sum([dico["LN"] for dico in bam_file.header["SQ"]])
    a = load_coverage(bam_file, pad=True)
    df = pd.DataFrame(a)
    df.chrom = df.chrom.str.decode(encoding = 'UTF-8')
    listMap = df[df.reads_all >= 1].reads_all

    dicoResume[sample]["Mean mapping Depth coverage"] = f"{mean(listMap):.2f}"
    dicoResume[sample]["Median mapping Depth coverage"] = f"{median(listMap):.2f}"
    dicoResume[sample]["Mean Genome Coverage"] = f"{(len(listMap)/dico_size_ref_genome[name_fasta_ref])*100:.2f}%"

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
        print(f"All CSV infos:\n{df}\n")
        df.to_csv(libsizeFile, index=False, sep=sep)

