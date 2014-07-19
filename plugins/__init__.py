import os
import glob
modules = [f for f in glob.glob(os.path.dirname(__file__)+"/*.py") if '__init__' not in f]