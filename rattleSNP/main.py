#!/usr/bin/env python3

from snakecdysis import main_wrapper
from rattleSNP import dico_tool

main = main_wrapper(**dico_tool)

if __name__ == '__main__':
    main()
