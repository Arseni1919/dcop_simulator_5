import matplotlib.pyplot as plt
import matplotlib
# import plotly.graph_objects as go
# import plotly.express as px
# import pandas as pd
import numpy as np
import random
import math
import copy
from collections import OrderedDict
# from scipy.spatial.distance import cdist
import abc
import os
import re

# import neptune.new as neptune

# import torch
# import torchvision
# import torchvision.transforms as T
# from torchvision.io import ImageReadMode

import itertools
from itertools import combinations, permutations
from collections import defaultdict, Counter
from pprint import pprint
from datetime import datetime
import time
import json

import cProfile
import pstats


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


colors_dict = {
    'random': 'blue',
    'dsa_mst': 'orange',
    'dsa_mst-breakdowns': 'tab:olive',
    'cadsa': 'green',
    'dssa': 'red',
    'ms': 'purple',
    'ms-breakdowns': 'brown',
    'CAMS (BUA)': 'pink',
    'CAMS': 'pink',
    'CAMS (OVP)': 'gray',
}

markers_dict = {
    'random': '.',
    'dsa_mst': 'v',
    'dsa_mst-breakdowns': 'v',
    'cadsa': '1',
    'dssa': '2',
    'ms': 's',
    'ms-breakdowns': 's',
    'CAMS (BUA)': '*',
    'CAMS': '*',
    'CAMS (OVP)': '8',
}