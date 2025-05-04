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

# функция для выполнения одного экземпляра sysbench 
def run_single_sysbench(duration, report_interval, output_queue, process_number, PATH_TO_SYSBENCH):
    
    print(PATH_TO_SYSBENCH)
    command = [
        PATH_TO_SYSBENCH,
        "cpu",
        "--threads=1",
        f"--time={duration}",
        f"--report-interval={report_interval}",
        "run"
    ]
    
    print(f"process {process_number} starting")
    output_queue.put(f"process starting")

    try:

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )


        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line,end='')
                output_queue.put(str(process_number) + ': ' + line)
        else:
             output_queue.put(f"{process_number} Error")

        process.wait()
        output_queue.put(f"{process_number}: finished, code {process.returncode}")
        print(f"{process_number} : finished, code {process.returncode}")

    except FileNotFoundError:
        print(f"{process_number} error: '{PATH_TO_SYSBENCH}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{process_number} error: {e}", file=sys.stderr)
        sys.exit(1)


# функция для записи логов из очереди в файл
def log_writer(output_queue, log_file_path):
    try:
        with open(log_file_path, "w", encoding="utf-8") as log_f:
            
            log_f.write(f"--- Starting CPU Test Log file ---\n")
            log_f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write("-" * 10 + '\n')
            while True:
                try:
                    # Получаем сообщение из очереди
                    line = output_queue.get(timeout=1)
                    
                    if line is None:  # Сигнал для завершения
                        log_f.write("-" * 20 + '\n')
                        log_f.write(f"--- End Sysbench CPU Test Log ---")
                        break
                    
                    log_f.write(line)
                    log_f.flush()
                except queue.Empty:
                    continue
    except Exception as e:
        print(f"Error writing to log file {log_file_path}: {e}", file=sys.stderr)


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

    processes = []
    start_time = time.time()

    # Запускаем n процессов sysbench
    for i in range(args.num_threads):
        process = multiprocessing.Process(
            target=run_single_sysbench,
            args=(args.time, args.report_interval, output_queue, i, PATH_TO_SYSBENCH)
        )
        processes.append(process)
        process.start()

        time.sleep(0.05)

    # Ждем завершения всех процессов sysbench
    for process in processes:
        process.join()

    # Сигнализируем потоку логгера, что пора завершаться
    output_queue.put(None)
    log_thread.join() # Ждем, пока логгер допишет все из очереди

    end_time = time.time()
    print("-" * 40)
    print(f"All {args.num_threads} sysbench instances finished.")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")
    print(f"Log file created at: {os.path.abspath(args.log_file)}")

    if args.graph:
        print("Graphing functionality is not implemented in this version.")
        # Сюда можно будет добавить вызов функции для построения графика
        # на основе данных из args.log_file


if __name__ == "__main__":
    main()
    
    # ./main.py --num-threads=3 --time=60
    # ./main.py --num-threads=1 --time=600