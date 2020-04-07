
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
        datetime(2020, 4,  4): {'hospitalized': 924, 'deceased': 140 },
        datetime(2020, 4,  4): {'hospitalized': 994, 'deceased': 150 }
}


ONEDAY = timedelta(1)
#
# cursor = FIT_START
# while cursor <= FIT_END:
# 	HOSP_FIT.append(FITNESS_SET[cursor]['hospitalized'])
# 	cursor += ONEDAY
