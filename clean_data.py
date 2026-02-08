import os

def clean_file(input_path, output_path, num_cols):
    print(f"Cleaning {input_path} -> {output_path}")
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    with open(output_path, 'w') as f:
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            if i == 0:
                # Header
                f.write(line + '\n')
                continue
            
            # Remove all quotes
            cleaned = line.replace('"', '')
            
            # Split by comma
            parts = cleaned.split(',')
            
            # Filter parts: sometimes there are extra commas because of the corruption
            # We want to merge the first two parts if the first one is 'DDO' and second is a number
            if len(parts) > 1 and parts[0] == 'DDO' and parts[1].strip().isdigit():
                parts[0] = parts[0] + ' ' + parts[1]
                parts.pop(1)
            
            # Now we might have many empty strings at the end. 
            # We only want num_cols.
            # But wait, some of the empty strings might be in the middle.
            
            # If we have more than num_cols, we should check if they are all empty at the end.
            if len(parts) > num_cols:
                # Keep only the first num_cols
                parts = parts[:num_cols]
            elif len(parts) < num_cols:
                # Pad with empty strings
                parts.extend([''] * (num_cols - len(parts)))
            
            f.write(','.join(parts) + '\n')

if __name__ == "__main__":
    if os.path.exists('data/raw_sparc/Table1.mrt'):
        clean_file('data/raw_sparc/Table1.mrt', 'data/raw_sparc/Table1_cleaned.csv', 19)
    if os.path.exists('data/raw_sparc/Table2.mrt'):
        clean_file('data/raw_sparc/Table2.mrt', 'data/raw_sparc/Table2_cleaned.csv', 10)