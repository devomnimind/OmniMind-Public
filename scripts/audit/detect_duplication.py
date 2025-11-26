import os
import hashlib


def hash_file_content(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def find_duplicates(root_dir, min_lines=5):
    hashes = {}
    duplicates = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") or file.endswith(".ts") or file.endswith(".tsx"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                        # Simple block hashing
                        for i in range(len(lines) - min_lines + 1):
                            block = "\n".join(lines[i : i + min_lines])
                            block_hash = hashlib.md5(block.encode("utf-8")).hexdigest()

                            if block_hash in hashes:
                                hashes[block_hash].append((path, i + 1))
                            else:
                                hashes[block_hash] = [(path, i + 1)]
                except:
                    pass

    for h, locs in hashes.items():
        if len(locs) > 1:
            # Filter out very common short blocks if needed
            duplicates.append(locs)

    return duplicates


if __name__ == "__main__":
    dups = find_duplicates("src", min_lines=10)  # Increase to 10 lines to reduce noise
    print(f"Found {len(dups)} duplicated blocks (>= 10 lines):")
    for d in dups:
        print(f"\n--- Duplicate Block ---")
        for path, line in d:
            print(f"  {path}:{line}")
