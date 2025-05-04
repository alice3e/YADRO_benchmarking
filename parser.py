#!/usr/bin/env python3

import re
import sys
from collections import defaultdict
import csv
import argparse

# смерть как она есть.....
INTERMEDIATE_REGEX = re.compile(r'^(\d+):\s+\[\s*(\d+)s\s*\]\s+.*?eps:\s*([\d.]+)')
FINAL_EPS_REGEX = re.compile(r'^(\d+):\s+events per second:\s*([\d.]+)')
OUTPUT_CSV_FILE = "report.csv"
DEFAULT_INPUT_FILE = 'sysbench_cpu_report.log'

def main(log_file_path):

    intermediate_results = defaultdict(dict)
    final_results = {}
    instance_ids_set = set()
    time_points_set = set()


    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match_inter = INTERMEDIATE_REGEX.match(line)
            if match_inter:
                instance_id_str = match_inter.group(1)
                time_s = int(match_inter.group(2))
                eps = float(match_inter.group(3))
                intermediate_results[time_s][instance_id_str] = eps
                instance_ids_set.add(instance_id_str)
                time_points_set.add(time_s)
                continue
            match_final = FINAL_EPS_REGEX.match(line)
            if match_final:
                instance_id_str = match_final.group(1)
                final_eps = float(match_final.group(2))
                final_results[instance_id_str] = final_eps
                instance_ids_set.add(instance_id_str)


    instance_ids = sorted(list(instance_ids_set), key=int)
    time_points = sorted(list(time_points_set))

    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)


        header = ['Time(s)'] + [f'Instance_{inst_id}' for inst_id in instance_ids]
        writer.writerow(header)

        for time_s in time_points:
            row = [f'{time_s}s']
            time_data = intermediate_results.get(time_s, {})
            for inst_id in instance_ids:
                eps_value = time_data.get(inst_id, '') 
                row.append(f"{eps_value:.2f}" if isinstance(eps_value, float) else eps_value)
            writer.writerow(row)


        final_row = ['Final_Avg_EPS']
        for inst_id in instance_ids:
             final_eps = final_results.get(inst_id, '')
      
             final_row.append(f"{final_eps:.2f}" if isinstance(final_eps, float) else final_eps)
        writer.writerow(final_row)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
    description="generate csv table from log file",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--file-name",
        type=str,
        required=False,
        default=DEFAULT_INPUT_FILE,
        help="log filename"
    )
    args = parser.parse_args()
    
    main(args.file_name)