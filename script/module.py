#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @package module.py
# @author Sebastien Ravel

##################################################
# Modules
import pysam
from collections import defaultdict, OrderedDict
import pandas as pd
from tempfile import NamedTemporaryFile
from pathlib import PosixPath, Path
from snakemake.io import load_configfile
from snakemake.utils import validate
from snakemake.io import glob_wildcards
import yaml
import pprint
import re
import os

################################################
# environment settings:
pd.set_option('display.max_column',None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_seq_items',None)
pd.set_option('display.max_colwidth', 500)
pd.set_option('expand_frame_repr', True)
# pd.options.display.width = None

################################################
# GLOBAL VARIABLES
ALLOW_FASTQ_EXT = (".fastq",".fq",".fq.gz",".fastq.gz")
AVAIL_CLEANING = ("ATROPOS", "FASTQC")
AVAIL_MAPPING = ("BWA_MEM", "BWA_SAMPE")

################################################
# GLOBAL functions
def get_last_version(version_RattleSNP):
    """Function for know the last version of RattleSNP in website
    Arguments:
        version_RattleSNP (str): the actual version of RattleSNP
    Returns:
        note: message if new version avail on the website
    Examples:
        >>> mess = get_last_version("1.2.0")
        >>> print(mess)
            Documentation avail at: https://RattleSNP.readthedocs.io/en/latest
            NOTE: The Latest version of RattleSNP 1.3.0 is available at https://github.com/sravel/RattleSNP/releases
    """
    try:
        from urllib.request import urlopen
        from re import search
        HTML = urlopen("https://github.com/sravel/RattleSNP/tags").read().decode('utf-8')
        lastRelease = \
        search('/sravel/RattleSNP/releases/tag/.*', HTML).group(0).split("/")[-1].split('"')[0]
        epilogTools = """Documentation avail at: https://RattleSNP.readthedocs.io/en/latest/ \n"""
        if version_RattleSNP != lastRelease:
            if lastRelease < version_RattleSNP:
                epilogTools += "\n** NOTE: This RattleSNP version is higher than the production version, you are using a dev version\n"
            elif lastRelease > version_RattleSNP:
                epilogTools += f"\nNOTE: The Latest version of RattleSNP {lastRelease} is available at https://github.com/sravel/RattleSNP/releases\n"
        return epilogTools
    except Exception as e:
        epilogTools = f"\n** ENABLE TO GET LAST VERSION, check internet connection\n{e}\n"
        return epilogTools


def get_version(RATTLESNP):
    """Read VERSION file to know current version
    Arguments:
        RATTLESNP (path): Path to RattleSNP install
    Returns:
        version: actual version read on the VERSION file
    Examples:
        >>> version = get_version("/path/to/install/RattleSNP")
        >>> print(version)
            1.3.0
    """
    with open(Path(RATTLESNP).joinpath("VERSION"), 'r') as version_file:
        return version_file.readline().strip()


def get_list_chromosome_names(fasta_file):
    """
            Return the list of sequence name on the fasta file.
            Work with Biopython and python version >= 3.5
    """
    from Bio import SeqIO
    return [*SeqIO.to_dict(SeqIO.parse(fasta_file,"fasta"))]


def get_files_ext(path, extensions, add_ext=True):
    """List of files with specify extension include on folder
    Arguments:
        path (str): a path to folder
        extensions (list or tuple): a list or tuple of extension like (".py")
        add_ext (bool): if True (default), file have extension

    Returns:
        :class:`list`: List of files name with or without extension , with specify extension include on folder
        :class:`list`: List of  all extension found

    Examples:
        >>> all_files, files_ext = get_files_ext("/path/to/fastq")
        >>> print(files_ext)
            [".fastq"]
     """
    if not (extensions, (list, tuple)) or not extensions:
        raise ValueError(f'ERROR RattleSNP: "extensions" must be a list or tuple not "{type(extensions)}"\n')
    tmp_all_files = []
    all_files = []
    files_ext = []
    for ext in extensions:
        tmp_all_files.extend(Path(path).glob(f"**/*{ext}"))

    for elm in tmp_all_files:
        ext = "".join(elm.suffixes)
        if ext not in files_ext:
            files_ext.append(ext)
        if add_ext:
            all_files.append(elm.as_posix())
        else:
            if len(elm.suffixes) > 1:

                all_files.append(Path(elm.stem).stem)
            else:
                all_files.append(elm.stem)
    return all_files, files_ext

################################################
# GLOBAL Class


class RattleSNP(object):
    """
    to read file config
    """

    def __init__(self, workflow, config, rattleSNP_path=None):
        # print(workflow.overwrite_clusterconfig)
        # culebront_path = Path(workflow.snakefile).parent
        # workflow is availbale only in __init
        self.snakefile = workflow.snakefile

        if not workflow.overwrite_configfiles:
            raise ValueError("ERROR CulebrONT: You need to use --configfile option to snakemake command line")
        else:
            self.path_config = workflow.overwrite_configfiles[0]
        self.cluster_config = workflow.overwrite_clusterconfig
        # self.cluster_config = load_configfile(culebront_path.joinpath("cluster_config.yaml"))
        self.tools_config = load_configfile(rattleSNP_path.joinpath("tools_path.yaml"))

        # print("\n".join(list(workflow.__dict__.keys())))
        # print(workflow.__dict__)

        # --- Verification Configuration Files --- #
        self.config = config
        self.fastq_path = None
        self.bam_path = None
        self.vcf_path = None
        self.samples = []
        self.run_RAXML = False

        # if provided fastq files
        self.fastq_gzip = False
        self.fastq_files_list = []
        self.fastq_files_ext = []

        self.cleaning_activated = False
        self.cleaning_tool = ""
        self.list_cleaning_tool_activated = []

        # mapping
        self.mapping_tool_activated = None
        self.mapping_activated = False
        self.mapping_stats_activated = False

        # calling
        self.calling_activated = False

        # filter
        self.vcf_filter_activated = False

        self.__check_config_dic()

    def get_config_value(self, section, key=None, subsection=None):
        if key:
            if subsection:
                return self.config[section][subsection][key]
            else:
                return self.config[section][key]
        else:
            return self.config[section]

    def set_config_value(self, section, key, value, subsection=None):
        if subsection:
            self.config[section][subsection][key] = value
        else:
            self.config[section][key] = value

    @property
    def export_use_yaml(self):
        """Use to print a dump config.yaml with corrected parameters"""

        def represent_dictionary_order(self, dict_data):
            return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())

        def setup_yaml():
            yaml.add_representer(OrderedDict, represent_dictionary_order)

        setup_yaml()
        return yaml.dump(self.config, default_flow_style=False, sort_keys=False, indent=4)

    def __check_dir(self, section, key, mandatory=[], subsection=None):
        """Check if path is a directory if not empty
            resolve path on config

        Arguments:
            section (str): the first level on config.yaml
            key (str): the final level on config.yaml
            mandatory (list tuple): a list or tuple with tools want mandatory info
            subsection (str): the second level on config.yaml (ie 3 level)

        Returns:
            :class:`list`: List of files name with or without extension , with specify extension include on folder
            :class:`list`: List of all extension found
        Raises:
            NotADirectoryError: If config.yaml data `path` does not exist.
        """
        path_value = self.get_config_value(section=section, key=key, subsection=subsection)
        if path_value:
            path = Path(path_value).resolve().as_posix() + "/"
            if (not Path(path).exists() or not Path(path).is_dir()) and key not in ["OUTPUT"]:
                raise NotADirectoryError(
                    f'CONFIG FILE CHECKING FAIL : in the "{section}" section{f", subsection {subsection}" if subsection else ""}, {key} directory "{path}" {"does not exist" if not Path(path).exists() else "is not a valid directory"}\n')
            else:
                self.set_config_value(section, key, path, subsection)
        elif len(mandatory) > 0:
            raise NotADirectoryError(
                f'CONFIG FILE CHECKING FAIL : in the "{section}" section{f", subsection {subsection}" if subsection else ""}, {key} directory "{path_value}" {"does not exist" if not Path(path_value).exists() else "is not a valid directory"} but is mandatory for tool: {" ".join(mandatory)}\n')

    def __check_file(self, section, key, mandatory=[], subsection=None):
        """Check if path is a file if not empty
        :return absolute path file"""
        path_value = self.get_config_value(section=section, key=key, subsection=subsection)
        path = Path(path_value).resolve().as_posix()
        if path:
            if not Path(path).exists() or not Path(path).is_file():
                raise FileNotFoundError(
                    f'CONFIG FILE CHECKING FAIL : in the {section} section{f", subsection {subsection}" if subsection else ""}, {key} file "{path}" {"does not exist" if not Path(path).exists() else "is not a valid file"}\n')
            else:
                self.set_config_value(section, key, path, subsection)
        elif len(mandatory) > 0:
            raise FileNotFoundError(
                f'CONFIG FILE CHECKING FAIL : in the "{section}" section{f", subsection {subsection}" if subsection else ""}, {key} file "{path_value}" {"does not exist" if not Path(path_value).exists() else "is not a valid file"} but is mandatory for tool: {" ".join(mandatory)}\n')

    def __var_2_bool(self, key, tool, to_convert):
        """convert to boolean"""
        if isinstance(type(to_convert), bool):
            return to_convert
        elif f"{to_convert}".lower() in ("yes", "true", "t"):
            return True
        elif f"{to_convert}".lower() in ("no", "false", "f"):
            return False
        else:
            raise TypeError(f'CONFIG FILE CHECKING FAIL : in the "{key}" section, "{tool}" key: "{to_convert}" is not a valid boolean\n')

    def __check_fastq_files(self):
        """check if fastq file have the same extension"""
        # check if fastq file for assembly
        self.fastq_path = self.get_config_value('DATA', 'FASTQ')
        self.fastq_files_list, fastq_files_list_ext = get_files_ext(self.fastq_path, ALLOW_FASTQ_EXT)
        if not self.fastq_files_list:
            raise ValueError(
                f"CONFIG FILE CHECKING FAIL : you need to append at least on fastq with extension on {ALLOW_FASTQ_EXT}\n")
        # check if all fastq have the same extension
        if len(fastq_files_list_ext) > 1:
            raise ValueError(
                f"CONFIG FILE CHECKING FAIL :please check 'DATA' section, key 'FASTQ', use only one extension format from {fastq_files_list_ext} found\n")
        else:
            self.fastq_files_ext = fastq_files_list_ext[0]
        # check if fastq are gzip
        if "gz" in self.fastq_files_ext:
            self.fastq_gzip = True

    def __build_tools_activated(self, key, allow, mandatory=False):
        tools_activate = []
        for tool, activated in self.config[key].items():
            if tool in allow:
                boolean_activated = self.__var_2_bool(key, tool, activated)
                if boolean_activated:
                    tools_activate.append(tool)
                    self.config[key][tool] = boolean_activated
            else:
                raise ValueError(f'CONFIG FILE CHECKING FAIL for key "{key}": {tool} not avail on RattleSNP\n')
        if len(tools_activate) == 0 and mandatory:
            raise ValueError(f"CONFIG FILE CHECKING FAIL : you need to set True for at least one {key} from {allow}\n")
        return tools_activate

    def __check_config_dic(self):
        """Configuration file checking"""
        # check output mandatory directory
        self.__check_dir(section="DATA", key="OUTPUT")

        # check cleaning activation
        self.list_cleaning_tool_activated = self.__build_tools_activated("CLEANING", AVAIL_CLEANING)
        if len(self.list_cleaning_tool_activated) > 0:
            self.cleaning_tool = "_"+self.list_cleaning_tool_activated[0]
            self.cleaning_activated = True
        elif len(self.list_cleaning_tool_activated) > 1:
            raise ValueError(f'CONFIG FILE CHECKING FAIL for section "CLEANING": please activate only one cleaning tool avail\n')

        # check mapping activation, if not use folder name to set self.mapping_tool_activated instead of mapping tool
        self.mapping_activated = self.__var_2_bool(tool="MAPPING", key="ACTIVATE", to_convert=self.get_config_value(section="MAPPING", key="ACTIVATE"))
        if self.mapping_activated:
            self.mapping_stats_activated = self.__var_2_bool(tool="MAPPING", key="BUILD_STATS", to_convert=self.get_config_value(section="MAPPING", key="BUILD_STATS"))
            self.mapping_tool_activated = self.get_config_value(section="MAPPING", key="TOOL")
            if self.mapping_tool_activated not in AVAIL_MAPPING:
                raise ValueError(f'CONFIG FILE CHECKING FAIL for section "MAPPING" key "TOOL": {self.mapping_tool_activated} not avail on RattleSNP\n')

        # if cleaning or mapping check fastq path and
        if self.cleaning_activated or self.mapping_activated:
            self.__check_dir(section="DATA", key="FASTQ")
            self.__check_fastq_files()
            self.samples, = glob_wildcards(f"{self.fastq_path}{{fastq}}_R1{self.fastq_files_ext}", followlinks=True)
            for sample in self.samples:
                if not Path(f"{self.fastq_path}{sample}_R2{self.fastq_files_ext}").exists():
                    ValueError(f"DATA CHECKING FAIL : The samples '{sample}' are single-end, please only use paired data: \n")
            # check reference file
            self.__check_file(section="DATA", key="REFERENCE_FILE")

        # check SNP calling activation:
        self.calling_activated = self.__var_2_bool(tool="SNPCALLING", key="", to_convert=self.get_config_value(section="SNPCALLING"))

        if not self.mapping_activated and self.calling_activated:
            self.__check_dir(section="DATA", key="BAM")
            self.bam_path = self.get_config_value(section="DATA", key="BAM")
            # self.mapping_tool_activated = Path(self.bam_path).stem
            self.samples, = glob_wildcards(f"{self.bam_path}{{bam}}.bam", followlinks=True)

        # check VCF filter activation
        self.vcf_filter_activated = self.__var_2_bool(tool="FILTER", key="", to_convert=self.get_config_value(section="FILTER"))
        # If only VCF filtration get vcf path
        if not self.mapping_activated and not self.calling_activated and self.vcf_filter_activated:
            self.__check_file(section="DATA", key="VCF")
            self.vcf_path = self.get_config_value(section="DATA", key="VCF")

        self.run_RAXML = self.__var_2_bool(tool="RAXML", key="", to_convert=self.get_config_value(section="RAXML"))

        # check mitochondrial name is in fasta is not Nome
        self.mito_name = self.get_config_value('PARAMS', 'MITOCHONDRIAL_NAME')
        chromosome_list = get_list_chromosome_names(self.get_config_value('DATA', 'REFERENCE_FILE'))
        if self.mito_name and self.mito_name not in chromosome_list:
            raise NameError(
                f'CONFIG FILE CHECKING FAIL : in the "PARAMS" section, "MITOCHONDRIAL_NAME" key: the name "{self.mito_name}" is not in fasta file {self.get_config_value("DATA", "REFERENCE_FILE")}\n')

    def __repr__(self):
        return f"{self.__class__}({pprint.pprint(self.__dict__)})"


def parse_idxstats(files_list = None, out_csv = None, sep="\t"):
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


def check_mapping_stats(bam, out_csv, sep = "\t"):
    from numpy import median, mean
    from pysamstats import load_coverage
    dico_size_ref_genome = {}
    dicoResume = defaultdict(OrderedDict)
    # for bam in bam_files:
    if not os.path.exists(Path(bam).as_posix()+".bai"): pysam.index(Path(bam).as_posix())
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
    df = (pd.read_csv(f, sep=sep) for f in csv_files)
    df = pd.concat(df)
    df.rename(columns={'Unnamed: 0':'Samples'}, inplace=True)
    with open(csv_file, "w") as libsizeFile:
        print(f"All CSV infos:\n{df}\n")
        df.to_csv(libsizeFile, index=False, sep=sep)

