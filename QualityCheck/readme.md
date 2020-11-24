# Welcome

There are two main functions in the QualityCheck module, it is split into training and evaluation. To do the evalutaion we need to train model a monophone accoustic model, allthough slightly tweaked. To do so change to a the approptiate paths in config.py and run "train_accoustic_model.py".

To evaluate a corpus a create a report use runQC.py e.g. "python3 runQC.py --name small_test". Paths to corpus and metadatafile are set in config.py.