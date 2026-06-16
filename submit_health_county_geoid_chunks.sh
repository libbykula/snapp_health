#!/bin/bash
#SBATCH --job-name=ht_county_chunk
#SBATCH --time=2:30:00
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem=4G
#SBATCH --array=0-0   # we overwrite this on submit
#SBATCH --output=logs/slurm-%A-%x.out

cd ~/gep_health/scripts
module load conda
source ~/.bashrc
conda activate /users/3/kula0049/.conda/envs/gdalfix

CHUNKS_FILE=usa_metro_county_chunks.txt
LINES=$(wc -l < $CHUNKS_FILE)

# SLURM automatically replaces array max when launched with --array
CHUNK=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $CHUNKS_FILE)

/users/3/kula0049/.conda/envs/gdalfix/bin/python run_chunk_county_prev_linear_v03.py $CHUNK
