
from datetime import datetime, timedelta

# FIT_START = datetime(2020, 3, 9)
# FIT_END = datetime(2020, 5, 2)
# # HOSP_FIT = [38, 44, 58, 58, 72, 84, 148, 176, 239, 274]
# HOSP_FIT = []
# #DEAD_FIT = [2, 4, 5, 6, 7, 11, 19, 24, 31, 44]

COLORADO_ACTUAL = {
        datetime(2020, 3, 13): {'hospitalized': 13 , 'deceased': 2   },
        datetime(2020, 3, 14): {'hospitalized': 18 , 'deceased': 3   },
        datetime(2020, 3, 15): {'hospitalized': 20 , 'deceased': 4   },
        datetime(2020, 3, 16): {'hospitalized': 26 , 'deceased': 4   },
        datetime(2020, 3, 17): {'hospitalized': 32 , 'deceased': 4   },
        datetime(2020, 3, 18): {'hospitalized': 41 , 'deceased': 7   },
        datetime(2020, 3, 19): {'hospitalized': 53 , 'deceased': 9   },
        datetime(2020, 3, 20): {'hospitalized': 71 , 'deceased': 11  },
        datetime(2020, 3, 21): {'hospitalized': 97 , 'deceased': 19  },
        datetime(2020, 3, 22): {'hospitalized': 126, 'deceased': 23  },
        datetime(2020, 3, 23): {'hospitalized': 169, 'deceased': 30  },
        datetime(2020, 3, 24): {'hospitalized': 205, 'deceased': 35  },
        datetime(2020, 3, 25): {'hospitalized': 263, 'deceased': 46  },
        datetime(2020, 3, 26): {'hospitalized': 326, 'deceased': 62  },
        datetime(2020, 3, 27): {'hospitalized': 391, 'deceased': 73  },
        datetime(2020, 3, 28): {'hospitalized': 451, 'deceased': 88  },
        datetime(2020, 3, 29): {'hospitalized': 542, 'deceased': 95  },
        datetime(2020, 3, 30): {'hospitalized': 640, 'deceased': 102 },
        datetime(2020, 3, 31): {'hospitalized': 714, 'deceased': 110 },
        datetime(2020, 4,  1): {'hospitalized': 784, 'deceased': 122 },
        datetime(2020, 4,  2): {'hospitalized': 861, 'deceased': 131 },
        datetime(2020, 4,  3): {'hospitalized': 899, 'deceased': 136 },
        datetime(2020, 4,  4): {'hospitalized': 924, 'deceased': 140 }
}




IHME_0325 = {
    datetime(2020, 3,  9): {'hospitalized': 11,   'icu':    3 },
    datetime(2020, 3, 10): {'hospitalized': 22,   'icu':    5 },
    datetime(2020, 3, 11): {'hospitalized': 22,   'icu':    5 },
    datetime(2020, 3, 12): {'hospitalized': 35,   'icu':    8 },
    datetime(2020, 3, 13): {'hospitalized': 39,   'icu':    9 },
    datetime(2020, 3, 14): {'hospitalized': 41,   'icu':    9 },
    datetime(2020, 3, 15): {'hospitalized': 54,   'icu':   11 },
    datetime(2020, 3, 16): {'hospitalized': 80,   'icu':   17 },
    datetime(2020, 3, 17): {'hospitalized': 93,   'icu':   20 },
    datetime(2020, 3, 18): {'hospitalized': 159,  'icu':   34 },
    datetime(2020, 3, 19): {'hospitalized': 187,  'icu':   40 },
    datetime(2020, 3, 20): {'hospitalized': 269,  'icu':   58 },
    datetime(2020, 3, 21): {'hospitalized': 292,  'icu':   63 },
    datetime(2020, 3, 22): {'hospitalized': 440,  'icu':   99 },
    datetime(2020, 3, 23): {'hospitalized': 477,  'icu':  105 },
    datetime(2020, 3, 24): {'hospitalized': 656,  'icu':  143 },
    datetime(2020, 3, 25): {'hospitalized': 813,  'icu':  180 },
    datetime(2020, 3, 26): {'hospitalized': 990,  'icu':  210 },
    datetime(2020, 3, 27): {'hospitalized': 1207, 'icu':  259 },
    datetime(2020, 3, 28): {'hospitalized': 1448, 'icu':  302 },
    datetime(2020, 3, 29): {'hospitalized': 1747, 'icu':  370 },
    datetime(2020, 3, 30): {'hospitalized': 2040, 'icu':  416 },
    datetime(2020, 3, 31): {'hospitalized': 2406, 'icu':  500 },
    datetime(2020, 4,  1): {'hospitalized': 2775, 'icu':  559 },
    datetime(2020, 4,  2): {'hospitalized': 3160, 'icu':  634 },
    datetime(2020, 4,  3): {'hospitalized': 3608, 'icu':  712 },
    datetime(2020, 4,  4): {'hospitalized': 4044, 'icu':  792 },
    datetime(2020, 4,  5): {'hospitalized': 4550, 'icu':  872 },
    datetime(2020, 4,  6): {'hospitalized': 4991, 'icu':  950 },
    datetime(2020, 4,  7): {'hospitalized': 5522, 'icu': 1027 },
    datetime(2020, 4,  8): {'hospitalized': 5968, 'icu': 1099 },
    datetime(2020, 4,  9): {'hospitalized': 6427, 'icu': 1164 },
    datetime(2020, 4, 10): {'hospitalized': 6861, 'icu': 1221 },
    datetime(2020, 4, 11): {'hospitalized': 7260, 'icu': 1268 },
    datetime(2020, 4, 12): {'hospitalized': 7616, 'icu': 1304 },
    datetime(2020, 4, 13): {'hospitalized': 7922, 'icu': 1329 },
    datetime(2020, 4, 14): {'hospitalized': 8171, 'icu': 1341 },
    datetime(2020, 4, 15): {'hospitalized': 8356, 'icu': 1340 },
    datetime(2020, 4, 16): {'hospitalized': 8472, 'icu': 1327 },
    datetime(2020, 4, 17): {'hospitalized': 8520, 'icu': 1302 },
    datetime(2020, 4, 18): {'hospitalized': 8496, 'icu': 1265 },
    datetime(2020, 4, 19): {'hospitalized': 8400, 'icu': 1218 },
    datetime(2020, 4, 20): {'hospitalized': 8239, 'icu': 1162 },
    datetime(2020, 4, 21): {'hospitalized': 8016, 'icu': 1098 },
    datetime(2020, 4, 22): {'hospitalized': 7735, 'icu': 1029 },
    datetime(2020, 4, 23): {'hospitalized': 7404, 'icu':  956 },
    datetime(2020, 4, 24): {'hospitalized': 7033, 'icu':  880 },
    datetime(2020, 4, 25): {'hospitalized': 6627, 'icu':  804 },
    datetime(2020, 4, 26): {'hospitalized': 6196, 'icu':  727 },
    datetime(2020, 4, 27): {'hospitalized': 5748, 'icu':  653 },
    datetime(2020, 4, 28): {'hospitalized': 5292, 'icu':  582 },
    datetime(2020, 4, 29): {'hospitalized': 4836, 'icu':  514 },
    datetime(2020, 4, 30): {'hospitalized': 4385, 'icu':  451 },
    datetime(2020, 5,  1): {'hospitalized': 3948, 'icu':  392 },
    datetime(2020, 5,  2): {'hospitalized': 3527, 'icu':  339 }
}

ONEDAY = timedelta(1)
#
# cursor = FIT_START
# while cursor <= FIT_END:
# 	HOSP_FIT.append(FITNESS_SET[cursor]['hospitalized'])
# 	cursor += ONEDAY
