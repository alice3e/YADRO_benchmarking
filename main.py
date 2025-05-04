#!/usr/bin/env python3

import argparse
import shutil
import sys
import subprocess
import multiprocessing
import threading
import queue
import time
import os


DEFAULT_REPORT_INTERVAL = 5
DEFAULT_LOG_FILE = "sysbench_cpu_report.log"
PATH_TO_SYSBENCH = None

def log_writer():
    pass

def main():
    
    parser = argparse.ArgumentParser(
        description="Run multiple single-threaded sysbench CPU tests in parallel and log intermediate results.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        required=True,
        help="Number of parallel sysbench instances to run (each with --threads=1)."
    )
    parser.add_argument(
        "--time",
        type=int,
        required=True,
        help="Duration of each sysbench test in seconds."
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=DEFAULT_REPORT_INTERVAL,
        help="Interval for sysbench intermediate reports in seconds."
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=DEFAULT_LOG_FILE,
        help="Path to the log file for intermediate results."
    )
    parser.add_argument(
        "--graph",
        action="store_true", 
    )

    args = parser.parse_args()
    
    #print(args)

    PATH_TO_SYSBENCH = shutil.which('sysbench')
    
    if not PATH_TO_SYSBENCH:
        print(f"Error: '{PATH_TO_SYSBENCH}' not found. install it", file=sys.stderr)
        sys.exit(1)
    else:
        print(f'sysbench found - {PATH_TO_SYSBENCH}')
    
    print(f"Starting {args.num_threads} parallel sysbench with time {args.time} seconds")
    print(f"Reports every {args.report_interval} seconds")
    print(f"Logging to {args.log_file}")


    # очередь для сообщений
    output_queue = multiprocessing.Queue()

    # поток для записи логов
    log_thread = threading.Thread(target=log_writer, args=(output_queue, args.log_file))
    log_thread.start()

if __name__ == "__main__":
    main()
    
    # ./main.py --num-threads=3 --time=60
    # ./main.py --num-threads=1 --time=600