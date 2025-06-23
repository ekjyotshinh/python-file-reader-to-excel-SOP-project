import re
import pandas as pd


def split_runs(content):
    # Split using lookahead: every time we encounter "Total RAM" -- just a way to seperate out multiple runs, maybe there's a bettter way but this works

    runs = re.split(r'Total RAM', content)
    return [run.strip() for run in runs if run.strip()]


def parse_run(run_text):
    # Instance name
    instance_match = re.search(r'Input file is .*\/(.+?\.sop)', run_text)
    if not instance_match:
        instance_match = re.search(r'^(.*\.sop)', run_text, re.MULTILINE)
    instance = instance_match.group(1).strip() if instance_match else 'Unknown'

    # LKH best entry Cost
    lkh_costs = re.findall(
        r'Best Cost temp\s*=\s*(\d+)\s+updated by LKH', run_text)
    final_lkh_cost = float(lkh_costs[-1]) if lkh_costs else None

    # Time taken for LKH to find its best entry
    lkh_find_time = re.findall(r'setting last updated at.*?([\d.]+)', run_text)
    final_lkh_find_time = float(lkh_find_time[-1]) if lkh_find_time else None

    # Enumerated nodes
    nodes_match = re.search(r'Total enumerated nodes:\s+(\d+)', run_text)
    enumerated_nodes = int(nodes_match.group(1)) if nodes_match else None

    # Extract gp const
    gp_const_match = re.search(r'gp const:\s*(\d+)', run_text, re.IGNORECASE)
    gp_const = int(gp_const_match.group(1)) if gp_const_match else None

    # Extract gp remaining
    gp_remaining_match = re.search(
        r'gp remaining:\s*(\d+)', run_text, re.IGNORECASE)
    gp_remaining = int(gp_remaining_match.group(
        1)) if gp_remaining_match else None

    # Extract percentage of work done
    percent_work_done_match = re.search(
        r'Percentage of work done:\s*(\d+)%', run_text, re.IGNORECASE)
    percent_work_done = int(percent_work_done_match.group(
        1)) if percent_work_done_match else None

    # Final Cost and Param (line after active time)
    final_cost, final_time = None, None

    # cost and time appear after "active time: ..."
    active_time_pattern = re.compile(
        r'active time:\s*[\d.]+\s*\n([^\n]+)', re.MULTILINE)

    active_line_match = active_time_pattern.search(run_text)

    if active_line_match:
        try:
            values = [v.strip()
                      for v in active_line_match.group(1).split(",") if v.strip()]
            # Parse as float or int as needed
            if len(values) >= 2:
                final_cost = int(float(values[0]))
                final_time = float(values[1])
        except Exception as e:
            print("Error parsing final cost/time:", e)
    # During reserch more parameters might be needed to make a meaningful conclusion, or formatting in the log file might change, so just update it accordingly
    return {
        'Instance': instance,
        'Final Cost': final_cost,
        'Final Time': str(final_time) + ' sec' if final_time is not None else None,
        'Enumerated Nodes': enumerated_nodes,
        'LKH Find Time': str(final_lkh_find_time) + ' sec' if final_lkh_find_time is not None else None,
        'LKH final cost': final_lkh_cost,
        'Global Pool Size': gp_const,
        'Remaining in Global Pool': gp_remaining,
        'Percentage work Done': str(percent_work_done) + '%' if percent_work_done is not None else None,
    }


def extract_multiple_runs(input_path):
    with open(input_path, 'r') as f:
        content = f.read()

    runs = split_runs(content)

    parsed_data = []

    for i, run in enumerate(runs):
        if i == 0:
            # the first partision would not have a data for the run, since the spliting logic cuts it off before the run data is present there
            continue
        parsed = parse_run(run)
        parsed_data.append(parsed)

    return parsed_data


def save_to_excel(data_list, output_path):
    df = pd.DataFrame(data_list)
    df.to_excel(output_path, index=False)
    # print(f"Saved {len(data_list)} parsed runs to {output_path}")


# execution
if __name__ == "__main__":
    # TODO : Update the names here to point to the the correct files
    input_file = "input.log"
    output_file = "output.xlsx"

    data = extract_multiple_runs(input_file)
    save_to_excel(data, output_file)
