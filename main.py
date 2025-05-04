#!/usr/bin/env python3

import argparse


DEFAULT_REPORT_INTERVAL = 5
DEFAULT_LOG_FILE = "sysbench_cpu_report.log"
SYSBENCH_COMMAND = "/usr/lib/sysbench"


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
        action="store_true", # Флаг, не требует значения
    )

    args = parser.parse_args()


if __name__ == "__main__":
    main()