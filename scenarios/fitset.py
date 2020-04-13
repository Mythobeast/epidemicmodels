
from datetime import datetime, timedelta

# FIT_START = datetime(2020, 3, 9)
# FIT_END = datetime(2020, 5, 2)
# # HOSP_FIT = [38, 44, 58, 58, 72, 84, 148, 176, 239, 274]
# HOSP_FIT = []
# #DEAD_FIT = [2, 4, 5, 6, 7, 11, 19, 24, 31, 44]

COLORADO_ACTUAL = {
        datetime(2020, 3, 13): {'hospitalized':  13, 'deceased':   2 },
        datetime(2020, 3, 14): {'hospitalized':  18, 'deceased':   3 },
        datetime(2020, 3, 15): {'hospitalized':  20, 'deceased':   4 },
        datetime(2020, 3, 16): {'hospitalized':  26, 'deceased':   4 },
        datetime(2020, 3, 17): {'hospitalized':  32, 'deceased':   4 },
        datetime(2020, 3, 18): {'hospitalized':  41, 'deceased':   7 },
        datetime(2020, 3, 19): {'hospitalized':  53, 'deceased':   9 },
        datetime(2020, 3, 20): {'hospitalized':  71, 'deceased':  11 },
        datetime(2020, 3, 21): {'hospitalized':  98, 'deceased':  20 },
        datetime(2020, 3, 22): {'hospitalized': 128, 'deceased':  24 },
        datetime(2020, 3, 23): {'hospitalized': 171, 'deceased':  31 },
        datetime(2020, 3, 24): {'hospitalized': 207, 'deceased':  36 },
        datetime(2020, 3, 25): {'hospitalized': 266, 'deceased':  47 },
        datetime(2020, 3, 26): {'hospitalized': 329, 'deceased':  63 },
        datetime(2020, 3, 27): {'hospitalized': 397, 'deceased':  75 },
        datetime(2020, 3, 28): {'hospitalized': 458, 'deceased':  90 },
        datetime(2020, 3, 29): {'hospitalized': 551, 'deceased':  97 },
        datetime(2020, 3, 30): {'hospitalized': 653, 'deceased': 104 },
        datetime(2020, 3, 31): {'hospitalized': 732, 'deceased': 112 },
        datetime(2020, 4,  1): {'hospitalized': 812, 'deceased': 125 },
        datetime(2020, 4,  2): {'hospitalized': 896, 'deceased': 136 },
        datetime(2020, 4,  3): {'hospitalized': 943, 'deceased': 142 },
        datetime(2020, 4,  4): {'hospitalized': 973, 'deceased': 146 },
        datetime(2020, 4,  4): {'hospitalized': 994, 'deceased': 150 }
}


ONEDAY = timedelta(1)
#
# cursor = FIT_START
# while cursor <= FIT_END:
# 	HOSP_FIT.append(FITNESS_SET[cursor]['hospitalized'])
# 	cursor += ONEDAY
