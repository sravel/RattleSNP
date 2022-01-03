#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from snakemake.io import load_configfile
from snakemake.io import glob_wildcards
from collections import OrderedDict
import yaml
import pprint
from rattleSNP.global_variable import *
from rattleSNP.usefull_function import *
################################################
# GLOBAL Class


class RattleSNP(object):
    """
    to read file config
    """

    def __init__(self, workflow, config):
        # workflow is availbale only in __init
        self.snakefile = workflow.main_snakefile
        self.tools_config = None
        self.cluster_config = None

        if not workflow.overwrite_configfiles:
            raise ValueError("ERROR RattleSNP: You need to use --configfile option to snakemake command line")
        else:
            self.path_config = workflow.overwrite_configfiles[0]

        self.load_tool_cluster_config()
        self.load_tool_configfile()

        ### USE FOR DEBUG
        # pprint.pprint("\n".join(list(workflow.__dict__.keys())))
        # pprint.pprint(workflow.__dict__)
        # exit()

        # --- Verification Configuration Files --- #
        self.config = config
        self.fastq_path = None
        self.bam_path = None
        self.vcf_path = None
        self.samples = []
        self.run_RAXML = False
        self.run_RAXML_NG = False

        self.CHROMOSOMES = []
        self.CHROMOSOMES_WITHOUT_MITO = []

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

    def load_tool_cluster_config(self):
        if RATTLESNP_USER_CLUSTER_CONFIG.exists() and not RATTLESNP_ARGS_CLUSTER_CONFIG.exists():
            self.cluster_config = load_configfile(RATTLESNP_USER_CLUSTER_CONFIG)
        elif RATTLESNP_ARGS_CLUSTER_CONFIG.exists():
            self.cluster_config = load_configfile(RATTLESNP_ARGS_CLUSTER_CONFIG)
            RATTLESNP_ARGS_CLUSTER_CONFIG.unlink()
        else:
            self.cluster_config = load_configfile(RATTLESNP_CLUSTER_CONFIG)

    def load_tool_configfile(self):
        if RATTLESNP_USER_TOOLS_PATH.exists() and not RATTLESNP_ARGS_TOOLS_PATH.exists():
            self.tools_config = load_configfile(RATTLESNP_USER_TOOLS_PATH)
        elif RATTLESNP_ARGS_TOOLS_PATH.exists():
            self.tools_config = load_configfile(RATTLESNP_ARGS_TOOLS_PATH)
            RATTLESNP_ARGS_TOOLS_PATH.unlink()
        else:
            self.tools_config = load_configfile(RATTLESNP_TOOLS_PATH)

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
        self.run_RAXML_NG = self.__var_2_bool(tool="RAXML_NG", key="", to_convert=self.get_config_value(section="RAXML_NG"))

        # check mitochondrial name is in fasta is not Nome
        if self.cleaning_activated or self.mapping_activated or self.calling_activated:
            self.mito_name = self.get_config_value('PARAMS', 'MITOCHONDRIAL_NAME')
            self.CHROMOSOMES = get_list_chromosome_names(self.get_config_value('DATA', 'REFERENCE_FILE'))
            if self.mito_name and self.mito_name not in self.CHROMOSOMES:
                raise NameError(
                    f'CONFIG FILE CHECKING FAIL : in the "PARAMS" section, "MITOCHONDRIAL_NAME" key: the name "{self.mito_name}" is not in fasta file {self.get_config_value("DATA", "REFERENCE_FILE")}\n')
            self.CHROMOSOMES_WITHOUT_MITO = self.CHROMOSOMES.copy()
            if self.mito_name and self.mito_name in self.CHROMOSOMES:
                self.CHROMOSOMES_WITHOUT_MITO.remove(self.mito_name)

    def __repr__(self):
        return f"{self.__class__}({pprint.pprint(self.__dict__)})"

