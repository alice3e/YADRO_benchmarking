#!/bin/bash

MAIN_SCRIPT="main.py"
PARSER_SCRIPT="parser.py"
GRAPH_SCRIPT="graph.py"

LOG_FILE="sysbench_cpu_report.log"
CSV_FILE="report.csv"
GRAPH_FILE="graph.png"
REPORT_INTERVAL=5

if [[ $# -ne 2 ]]; then
  echo "Error: Incorrect number of arguments" >&2
  echo "Usage: <num_threads> <time_seconds>" >&2
  exit 1
fi

# --- Присвоение позиционных аргументов переменным ---
NUM_THREADS="$1"
TEST_TIME="$2"

# бекапим прошлые результаты
# например если несколько раз запускаем бенчмарк, то надо все переименовывать, чтобы не перезаписать
backup_file() {
  local base_filename=$1

  if [[ ! -e "$base_filename" ]]; then
    return 0 # Файла нет бэкапить нечего
  fi

  local i=1
  local backup_name=""
  # Ищем первый свободный номер для бэкапа
  while true; do
    backup_name="${base_filename}.${i}"
    if [[ ! -e "$backup_name" ]]; then
      echo "Renaming '$base_filename' to '$backup_name'"
      mv "$base_filename" "$backup_name"
      return 0
    fi
    ((i++))
  done
}

set -e

echo "--- Starting Benchmark ---"

# 1. Бэкап существующих файлов результатов
echo "Checking for taken filenames"
backup_file "$LOG_FILE"
backup_file "$CSV_FILE"
backup_file "$GRAPH_FILE"


echo ' '
echo ' '

# ПРО SUDO НЕ ЗАБЫВАЕМ
if sudo python3 "$MAIN_SCRIPT" --num-threads="$NUM_THREADS" --time="$TEST_TIME" --log-file="$LOG_FILE" --report-interval="$REPORT_INTERVAL"; then
  echo "benchmark completed successfully."
else
  echo "Error: benchmark failed." >&2
  exit 1
fi


echo ' '
echo ' '


echo "Running parser to generate $CSV_FILE from $LOG_FILE"
if python3 "$PARSER_SCRIPT"; then
   echo "parser completed successfully."
else
  echo "Error: parser failed." >&2
  exit 1
fi

echo ' '
echo ' '

echo "Running graph to generate $GRAPH_FILE from $CSV_FILE"
if python3 "$GRAPH_SCRIPT"; then
  echo "$GRAPH_SCRIPT completed successfully."
else
  echo "Error: graph failed." >&2
  exit 1
fi

echo ' '
echo ' '

echo "--- Benchmark Complete ---"
echo "Log file: $LOG_FILE"
echo "CSV report: $CSV_FILE"
echo "Graph image: $GRAPH_FILE"

exit 0