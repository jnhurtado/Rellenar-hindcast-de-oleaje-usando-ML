# -*- coding: utf-8 -*-
"""
Código predictor de oleaje
"""


import numpy as np
import matplotlib.pyplot as plt
import tensorflow
from tensorflow import keras
import funciones as fun
import os

data=fun.read_NCEP_txt("NCEP_Spectra_from_Partitions_33.0S_72W_197901to200912_check.dfs0", resample = False, freq = '3H', npart = 11)

