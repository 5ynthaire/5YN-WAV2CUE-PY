import sys
from datetime import timedelta
import argparse

def parse_time_to_seconds(time_str):
    time_str = time_str.strip().rstrip('s')
    if '.' in time_str:
        minutes_seconds, milliseconds = time_str.split('.')
        ms_part = milliseconds.ljust(3, '0')[:3]
        ms = round(float('0.' + ms_part) * 1000)
    else:
        minutes_seconds = time_str
        ms = 0
    
    parts = minutes_seconds.split(':')
    if len(parts) == 3:
        h, m, s = map(int, parts)
    elif len(parts) == 2:
        h = 0
        m, s = map(int, parts)
    else:
        raise ValueError("Invalid time format")
    
    return h * 3600 + m * 60 + s + ms / 1000.0

def seconds_to_time(seconds):
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = td.total_seconds() % 60
    ms = int(round((secs - int(secs)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d}.{ms:03d}"

def format_seconds_to_label(seconds):
    return f"{seconds:.3f}"

def read_input_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception:
        print("Error: Invalid input file")
        sys.exit(1)
    
    separator_found = False
    base_line = None
    tracks = []
    
    for line in lines:
        if line == '---':
            if separator_found:
                continue
            separator_found = True
            continue
        
        if not separator_found:
            if base_line is not None:
                print("Error: Multiple BASE lines found")
                sys.exit(1)
            base_line = line
        else:
            if ',' not in line:
                continue
            tracks.append(line)
    
    if base_line is None or not tracks:
        print("Error: Invalid input format - missing BASE or tracks")
        sys.exit(1)
    
    try:
        base_parts = base_line.split(',', 1)
        base_name = base_parts[0].strip()
        base_duration = parse_time_to_seconds(base_parts[1].strip())
        
        track_data = []
        for track_line in tracks:
            t_str, name = track_line.split(',', 1)
            track_duration = parse_time_to_seconds(t_str.strip())
            track_data.append((name.strip(), track_duration))
        
        return base_name, base_duration, track_data
    except ValueError:
        print("Error: Invalid line format in input file")
        sys.exit(1)

def calculate_boundaries(base_duration, track_data, cumulative_mode):
    track_count = len(track_data)
    
    if cumulative_mode:
        starts = [t for _, t in track_data]
        if not starts:
            print("Error: No tracks provided")
            sys.exit(1)
        if starts[0] != 0.0:
            print("Error: First track must start at 00:00:00.000")
            sys.exit(1)
        for i in range(1, len(starts)):
            if starts[i] <= starts[i-1]:
                print("Error: Track starts must be strictly increasing")
                sys.exit(1)
        if starts[-1] > base_duration:
            print(f"Error: Last track start {seconds_to_time(starts[-1])} exceeds file duration {seconds_to_time(base_duration)}")
            sys.exit(1)
        boundaries = starts + [base_duration]
        total_track_duration = base_duration
        adjustment_per_track = 0.0
        gap = 0.0
        return boundaries, total_track_duration, adjustment_per_track, gap, track_count
    
    # Duration mode
    total_track_duration = sum(t for _, t in track_data)
    gap = abs(base_duration - total_track_duration)
    threshold_green = 0.5 * track_count
    threshold_red = 1.0 * track_count
    
    if gap >= threshold_red:
        print(f"Error: Time mismatch too large ({gap:.3f}s >= {threshold_red:.3f}s)")
        sys.exit(1)
    elif gap >= threshold_green:
        response = input(f"Warning: Large time mismatch ({gap:.3f}s). Proceed? (y/N): ").lower()
        if response != 'y':
            print("Aborted by user")
            sys.exit(1)
    
    adjustment_per_track = (base_duration - total_track_duration) / track_count
    
    boundaries = [0.0]
    cumulative = 0.0
    for i, (_, duration) in enumerate(track_data):
        cumulative += duration + adjustment_per_track
        if i == len(track_data) - 1:
            boundaries.append(base_duration)
        else:
            boundaries.append(min(cumulative, base_duration))
    
    return boundaries, total_track_duration, adjustment_per_track, gap, track_count

def write_labels_file(boundaries, track_data):
    filename = "labels.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for i, (name, _) in enumerate(track_data):
            start = boundaries[i]
            end = boundaries[i + 1]
            f.write(f"{format_seconds_to_label(start)}\t{format_seconds_to_label(end)}\t{name}\n")
    return filename

def write_cue_file(boundaries, track_data, base_name):
    wav_filename = f"{base_name}.wav"
    filename = "tracks.cue"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('REM GENRE AudioCD\n')
        f.write('REM DATE 2025\n')
        f.write('TITLE Album_Title\n')
        f.write('PERFORMER Artist_Name\n')
        f.write(f'FILE "{wav_filename}" WAVE\n\n')
        
        for i, (name, _) in enumerate(track_data, 1):
            start_time = seconds_to_time(boundaries[i-1])
            f.write(f'  TRACK {i:02d} AUDIO\n')
            f.write(f'    TITLE "{name}"\n')
            f.write(f'    INDEX 01 {start_time}\n\n')
    return filename

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs='?', help='Input file with track timings')
    parser.add_argument('--labels', action='store_true', help='Generate labels.txt (default: tracks.cue)')
    parser.add_argument('--cumulative', action='store_true', help='Use cumulative start times')
    args = parser.parse_args()
    
    if not args.input_file:
        print("Usage: python wav_cue.py [input.txt | --cumulative input.txt | --labels input.txt]")
        sys.exit(1)
    
    generate_labels = args.labels
    cumulative_mode = args.cumulative
    
    base_name, base_duration, track_data = read_input_file(args.input_file)
    boundaries, track_total, adjustment_per_track, gap, track_count = calculate_boundaries(base_duration, track_data, cumulative_mode)
    
    if generate_labels:
        filename = write_labels_file(boundaries, track_data)
    else:
        filename = write_cue_file(boundaries, track_data, base_name)
    
    mode_str = "Cumulative" if cumulative_mode else "Duration"
    print(f"{mode_str} mode")
    print(f"{base_name} duration: {seconds_to_time(base_duration)}")
    print(f"Tracks sum: {seconds_to_time(track_total)}")
    print(f"Total difference: {gap:.3f}s")
    print(f"Track count: {track_count}")
    print("")
    if not cumulative_mode:
        print("Rounding error distribution summary:")
        print(f"  Adjustment per track: {adjustment_per_track:+.3f}s")
        print(f"  Total adjustment: {adjustment_per_track * track_count:+.3f}s")
    print(f"Generated: {filename}")
    print("")

if __name__ == "__main__":
    main()
