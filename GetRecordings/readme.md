# GetRecordings
This module enables easy gathering of all Samrómur related data. It can be used to download either a predetermined subset of data or the entirety of it. The data - which is collected on Samrómur and can be downloaded using these tools - is obviously the audio clips but accompanying the clips are their metadata which these tools are capable of getting as well.  
The main goal of this tool is to enable developers to get large amounts of data in bulk -  eliminating the tediousness and slow progress of manually downloading one clip at a time. It also handily gathers the exact metadata needed for the set of clips which was selected for download.

## Table of contents
- [GetRecordings](#getrecordings)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Running](#running)
    - [Small batches](#small-batches)
    - [Larger batches](#larger-batches)
    - [Arguments](#arguments)
    - [Credentials](#credentials)
  - [Files and folders](#files-and-folders)
  - [Authors/Credit](#authorscredit)
    - [Acknowledgements](#acknowledgements)


## Installation
The following Python packages are required for this module:
* boto3
* mysql-connector-python
* pandas
* tqdm
* uuid
* numpy
* soundfile
* pydub

They are also listed in requirements.txt. Therefore, you can easily install all of them by running the command `pip install -r requirements.txt`.

## Running
This module consists of five submodules which have their respective purposes. It is run via download.py which serves as an interface for GetRecordings and accepts arguments to tweak a variety of options as needed. The main submodule is extractor.py which contains all of the necessary functions while the others are, although necessary, support submodules.

### Small batches
If you intend to download a small handful of clips, it is recommended to simply run download.py using `python3 download.py` with arguments as desired.

### Larger batches
As the downloading process can become quite time and resource consuming - if you are working on a Linux cluster - it is recommended that you use workload manager such as Slurm. If you are using Slurm, you can use run.sh using `sbatch run.sh`. You can freely alter the Slurm parameters and download.py arguments in run.sh as needed.

### Arguments
Please refer to the descriptions of each argument in download.py. If anything is unclear, feel free to contact David Erik or Smári Freyr.

### Credentials
User credentials are required for access to the cloudbased data. For obvious reasons, these credentials are not stored on the GitHub repository. Please contact David Erik or Smári Freyr for the credentials file. It should be placed in the root of this module.

## Files and folders
- root
  - Contains the files needed for running
    - download.py
    - run.sh
    - requirements.txt for dependency installation
- modules
  - Contains the submodules of GetRecordings
- utils
  - Contains miscellaneous files
    - config.py for credentials access
  - oto
    - (O)ne (t)ime (o)nly scripts that perform something useful regarding the downloaded data but might or might not be needed again.

## Authors/Credit
Reykjavik University

- David Erik Mollberg <david.e.mollberg@gmail.com>
- Smári Freyr Guðmundsson <smarig@ru.is>

### Acknowledgements
"This project was funded by the Language Technology Programme for Icelandic 2019-2023. The programme, which is managed and coordinated by [Almannarómur](https://almannaromur.is/), is funded by the Icelandic Ministry of Education, Science and Culture."