from pathlib import Path
from collections import defaultdict, OrderedDict


def parse_flagstat_multi_report(files_list, out_csv="toto.csv", sep="\t"):
    """
    Take a list of files, parse the data assuming it's a flagstat file
    Returns csv file
    """
    import re
    from pathlib import Path
    from collections import defaultdict, OrderedDict
    import pandas as pd
    flagstat_regexes = {
        "total": r"(\d+) \+ (\d+) in total \(QC-passed reads \+ QC-failed reads\)",
        "secondary": r"(\d+) \+ (\d+) secondary",
        # "supplementary": r"(\d+) \+ (\d+) supplementary",
        "duplicates": r"(\d+) \+ (\d+) duplicates",
        # "mapped": r"(\d+) \+ (\d+) mapped \((.+):(.+)\)",
        "paired in sequencing": r"(\d+) \+ (\d+) paired in sequencing",
        # "read1": r"(\d+) \+ (\d+) read1",
        # "read2": r"(\d+) \+ (\d+) read2",
        "properly paired": r"(\d+) \+ (\d+) properly paired \((.+):(.+)\)",
        # "with itself and mate mapped": r"(\d+) \+ (\d+) with itself and mate mapped",
        "singletons": r"(\d+) \+ (\d+) singletons \((.+):(.+)\)",
        "mate mapped to a diff chr": r"(\d+) \+ (\d+) with mate mapped to a different chr",
        "mate mapped to a diff chr (mapQ >= 5)": r"(\d+) \+ (\d+) with mate mapped to a different chr mapQ>=5\)",
    }
    parsed_data = defaultdict(OrderedDict)
    # re_groups = ["passed", "failed", "passed_pct", "failed_pct"]
    re_groups = ["passed", "failed"]
    for file in files_list:
        file_str = Path(file).open("r").read()
        sample = Path(file).stem.split("_")[0]
        for k, r in flagstat_regexes.items():
            r_search = re.search(r, file_str, re.MULTILINE)
            if r_search:
                for i, j in enumerate(re_groups):
                    try:
                        key = "{}_{}".format(k, j)
                        val = r_search.group(i + 1).strip("% ")
                        parsed_data[sample][key] = float(val) if ("." in val) else int(val)
                    except IndexError:
                        pass  # Not all regexes have percentages
                    except ValueError:
                        parsed_data[sample][key] = float("nan")
        # Work out the total read count
        try:
            parsed_data[sample]["Total"] = parsed_data[sample]["total_passed"] + parsed_data[sample]["total_failed"]
            parsed_data[sample]["mapped_pass (%)"] = f'{(parsed_data[sample]["total_passed"]/parsed_data[sample]["flagstat_total"])*100:.2f}%'
            parsed_data[sample]["properly_paired (%)"] = f'{(parsed_data[sample]["properly paired_passed"]/parsed_data[sample]["flagstat_total"])*100:.2f}%'
        except KeyError as e:
            print(e)
            pass
    # return parsed_data
    dataframe_mapping_stats = pd.DataFrame.from_dict(parsed_data, orient='index')
    dataframe_mapping_stats.drop(dataframe_mapping_stats.filter(regex='_failed').columns, axis=1, inplace=True)
    dataframe_mapping_stats.columns = [name.replace("_passed", "") for name in dataframe_mapping_stats.columns]
    dataframe_mapping_stats.reset_index(level=0, inplace=True)
    dataframe_mapping_stats.rename({"index": 'Samples'}, axis='columns', inplace=True, errors="raise")
    with open(out_csv, "w") as out_csv_file:
        print(f"Library size:\n{dataframe_mapping_stats}\n")
        dataframe_mapping_stats.to_csv(out_csv_file, index=False, header=True, sep=sep)


def parse_idxstats(files_list=None, out_csv=None, sep="\t"):
    from pathlib import Path
    from collections import defaultdict, OrderedDict
    import pandas as pd
    dico_mapping_stats = defaultdict(OrderedDict)
    for csv_file in files_list:
        sample = Path(csv_file).stem.split("_")[0]
        df = pd.read_csv(csv_file, sep="\t", header=None, names=["chr", "chr_size", "map_paired", "map_single"], index_col=False)
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
    dataframe_mapping_stats.reset_index(level=0, inplace=True)
    dataframe_mapping_stats.rename({"index": 'Samples'}, axis='columns', inplace=True, errors="raise")
    with open(out_csv, "w") as out_csv_file:
        # print(f"Library size:\n{dataframe_mapping_stats}\n")
        dataframe_mapping_stats.to_csv(out_csv_file, index=False, sep=sep)


def get_genome_size(fasta_file):
    """
            Return the list of sequence name on the fasta file.
            Work with Biopython and python version >= 3.5
    """
    from Bio import SeqIO
    return sum([len(seq) for seq in SeqIO.to_dict(SeqIO.parse(fasta_file, "fasta")).values()])


def check_mapping_stats(ref, depth_file, out_csv, sep="\t"):
    from numpy import median, mean
    import pandas as pd
    genome_size = get_genome_size(ref)
    dicoResume = defaultdict(OrderedDict)

    sample = Path(depth_file).stem.split("_DEPTH")[0]
    listMap = []
    with open(depth_file, "r") as depth_file_open:
        for line in depth_file_open:
            chr, pos, depth = line.rstrip().split("\t")
            listMap.append(int(depth))
    dicoResume[sample]["Mean Depth"] = f"{mean(listMap):.2f}"
    dicoResume[sample]["Median Depth"] = f"{median(listMap):.2f}"
    dicoResume[sample]["Max Depth"] = f"{max(listMap):.2f}"
    dicoResume[sample]["%Mean Genome coverage"] = f"{(len(listMap)/genome_size)*100:.2f}"

    dataframe_mapping_stats = pd.DataFrame.from_dict(dicoResume, orient='index')
    dataframe_mapping_stats.reset_index(level=0, inplace=True)
    dataframe_mapping_stats.rename({"index": 'Samples'}, axis='columns', inplace=True, errors="raise")
    with open(out_csv, "w") as out_csv_file:
        # print(f"Library size:\n{dataframe_mapping_stats}\n")
        dataframe_mapping_stats.to_csv(out_csv_file, index=False, sep=sep)


def merge_samtools_depth_csv(csv_files, csv_file, sep="\t"):
    # dir = Path(csv_files)
    import pandas as pd
    df = (pd.read_csv(f, sep=sep) for f in csv_files)
    df = pd.concat(df)
    df.rename(columns={'Unnamed: 0': 'Samples'}, inplace=True)
    with open(csv_file, "w") as out_csv_file:
        # print(f"All CSV infos:\n{df}\n")
        df.to_csv(out_csv_file, index=False, sep=sep)


def tsv_per_chromosome(gvcf_files, tsv_file, chromosome, sep="\t"):
    import pandas as pd
    from pathlib import Path
    dico = {(Path(file).stem.split(chromosome)[0], file) for file in gvcf_files}
    df = pd.DataFrame.from_dict(dico)
    with open(tsv_file, "w") as out_tsv_file:
        # print(f"Library size:\n{dataframe_mapping_stats}\n")
        df.to_csv(out_tsv_file, index=False, header=False, sep=sep)
