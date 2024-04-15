import math
import os
from datetime import datetime


def find_non_empty_lines(input_file_path):
    with open(input_file_path, "r") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    lines.remove("WEBVTT")
    return lines


def insert_empty_between_timeframes(lines):
    new_lines = []
    for i in range(len(lines)):
        if lines[i].startswith("00:"):  # Check if the line is a time frame
            if i > 0 and lines[i - 1].startswith("00:") and new_lines[-1] != "":
                new_lines.append("")  # Insert an empty string
        new_lines.append(lines[i])  # Add the current line to the new list
    return new_lines


def check_first_timeframe(lines):
    start, end = lines[0].split(" --> ")
    start_time = datetime.strptime(start, "%H:%M:%S.%f")
    end_time = datetime.strptime(end, "%H:%M:%S.%f")
    duration = end_time - start_time
    if duration.total_seconds() < 1:
        removed_item = lines.pop(0)
    else:
        removed_item = None
    return lines, removed_item


def remove_timeframes(lines):
    return [line for line in lines if not line.startswith("00:")]


def only_timeframes(lines):
    return [line for line in lines if line.startswith("00:")]


def make_dict(lines):
    string_counts = {}
    count = 0
    for i, item in enumerate(lines):
        if item.strip():
            count += 1
            j = i
            while j + 1 < len(lines) and lines[j + 1] == "":
                count += 1
                j += 1
            string_counts[item] = count
            count = 0

    return string_counts


def key_divided_by_value(result_dict):
    result = []
    for key in result_dict:
        words = key.split()
        words_per_para = math.floor(len(words) / result_dict[key])
        words_per_line = math.ceil(words_per_para / 2)
        x = len(words) % result_dict[key]
        i = 0
        while i < len(words):
            if x > 0:
                result.append(words[i : i + words_per_line + 1])
                i += words_per_line + 1
                x -= 1
            else:
                result.append(words[i : i + words_per_line])
                i += words_per_line
    return result


def text_to_vtt(only_timeframes, key_divided_by_value, result_dict, input_file_path):
    if not only_timeframes or not key_divided_by_value or not result_dict:
        return []  # or handle the empty input case as needed
    list3 = [value for value in result_dict.values()]
    sum_list = sum(list3)
    if sum_list == 0:
        return []  # or handle the zero sum case as needed
    j = 0
    list4 = []

    for i in range(sum_list):
        k = 0
        try:
            list4.append(only_timeframes[i])
            while k < 1:
                try:
                    if any("." in item for item in key_divided_by_value[j]):
                        list4.append(key_divided_by_value[j])
                        list4.append(" ")
                        j += 1
                        break
                    else:
                        list4.append(key_divided_by_value[j])
                        j += 1
                        list4.append(key_divided_by_value[j])
                        j += 1
                        k += 1
                        list4.append(" ")
                except IndexError:
                    # Handle index out of range gracefully
                    print(
                        f"Index out of range in while loop. Skipping...{input_file_path}"
                    )
                    break
        except IndexError:
            # Handle index out of range gracefully
            print(f"Index out of range in for loop. Skipping...{input_file_path}")
            break
    list4.append(only_timeframes[-1])
    return list4


def new_vtt_file(text_to_vtt, input_file_path, removed_item):
    output_file_path = input_file_path[:-7] + ".vtt"
    with open(output_file_path, "w") as f:
        print("WEBVTT", file=f)
        print(" ", file=f)
        if removed_item:
            print(removed_item, file=f)
            print(" ", file=f)
        for item in text_to_vtt:
            if isinstance(item, list):
                print(" ".join(item), file=f)
            else:
                print(item, file=f)


def process_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".vtt"):
            input_file_path = os.path.join(folder_path, filename)
            process_single_file(input_file_path)


def process_single_file(input_file_path):
    lines = find_non_empty_lines(input_file_path)
    new_lines = insert_empty_between_timeframes(lines)
    new_lines, removed_item = check_first_timeframe(new_lines)
    lines_without_timeframes = remove_timeframes(new_lines)
    timeframes = only_timeframes(lines)
    result_dict = make_dict(lines_without_timeframes)
    divided_by_value = key_divided_by_value(result_dict)

    # Print lengths for debugging
    print(input_file_path)
    print("Length of timeframes:", len(timeframes))
    print("Length of divided_by_value:", len(divided_by_value))
    print("Length of result_dict:", len(result_dict))

    result = text_to_vtt(timeframes, divided_by_value, result_dict, input_file_path)
    new_vtt_file(result, input_file_path, removed_item)


folder_path = input("Enter the folder path: ")
process_files_in_folder(folder_path)
