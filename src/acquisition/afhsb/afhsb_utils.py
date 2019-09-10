DATAPATH = '/home/automation/afhsb_data'

# SOURCE_DIR: the directory which contains raw data
SOURCE_DIR = DATAPATH

# PARENT_TARGET_DIR: parent directory of the directory where aggregated data is to be stored
PARENT_TARGET_DIR = os.path.join(DATAPATH, "aggregated")

# name of the diagnosis-classification function
FN_NAME = 'flucat'

# TARGET_DIR: the directory where you'd like aggregated data to be stored
TARGET_DIR = os.path.join(PARENT_TARGET_DIR, 'agg_{}'.format(FN_NAME))