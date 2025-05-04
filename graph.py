#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_GRAPH_FILE = "graph.png"
DEFAULT_INPUT_FILE = "report.csv"

def main(csv_file_path):
    df = pd.read_csv(csv_file_path)

    df_intermediate = df[df['Time(s)'] != 'Final_Avg_EPS'].copy()
    #print(df_intermediate)
    df_intermediate['Time_Num'] = pd.to_numeric(df_intermediate['Time(s)'].astype(str).str.replace('s', '', regex=False), errors='coerce')
    #print(df_intermediate)
    df_intermediate.dropna(subset=['Time_Num'], inplace=True)
    #print(df_intermediate)
    df_intermediate['Time_Num'] = df_intermediate['Time_Num'].astype(int)
    df_intermediate.set_index('Time_Num', inplace=True)
    #print(df_intermediate)
    eps_columns = [col for col in df_intermediate.columns if col != 'Time(s)']
    for col in eps_columns:
        df_intermediate[col] = pd.to_numeric(df_intermediate[col], errors='coerce')

    fig, ax = plt.subplots(figsize=(12, 7))
    df_intermediate[eps_columns].plot(ax=ax)
    ax.set_title("Sysbench CPU EPS over Time")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Events Per Second (EPS)")
    ax.legend(title="sysbench ID", loc='best')
    plt.tight_layout()
    plt.savefig(OUTPUT_GRAPH_FILE)
    plt.close(fig)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
    description="generate graph from csv file",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--file-name",
        type=str,
        required=False,
        default=DEFAULT_INPUT_FILE,
        help="csv filename"
    )
    
    args = parser.parse_args()
    main(args.file_name)