import argparse
import zlib
import re



def decompress_blocks(raw_bytes):
    results = []
    offsets = [m.start() for m in re.finditer(b"\x78\xDA", raw_bytes)]
    for start in offsets:
        stream = raw_bytes[start:]
        decomp = zlib.decompressobj()
        try:
            data = decomp.decompress(stream)
            end_offset = start + len(stream) - len(decomp.unused_data)
            results.append({"start": start, "end": end_offset, "data": data})
        except zlib.error:
            continue
    return offsets, results

def main():
    parser = argparse.ArgumentParser(description="Extract zlib blocks from raw binary .ref file")
    parser.add_argument("ref_file", help="Path to the raw binary .ref file")
    parser.add_argument("--write", action="store_true",
                        help="Write each decompressed block to a file")
    parser.add_argument("--out-prefix", default="block",
                        help="Prefix for output files if --write is used")
    args = parser.parse_args()

    # Read raw binary
    with open(args.ref_file, "rb") as f:
        raw_bytes = f.read()

    offsets, blocks = decompress_blocks(raw_bytes)
    print(f"Found {len(offsets)} zlib headers, decompressed {len(blocks)} blocks")
    print(f"Signal_Name,Message_ID,Units,StartBit,Length,Offset,Scale,Max,Min,Type,Endian,DLC")
    for i, b in enumerate(blocks):
        print(f"\n--- Block {i} (bytes {b['start']}-{b['end']}) ---")
        try:
            print(b["data"].decode("utf-8"))
        except UnicodeDecodeError:
            print(b["data"].hex())

        if args.write:
            ext = "txt"
            try:
                b["data"].decode("utf-8")
            except UnicodeDecodeError:
                ext = "bin"
            out_path = f"{args.out_prefix}{i}.{ext}"
            with open(out_path, "wb") as f:
                f.write(b["data"])
            print(f"[wrote {out_path}]")

if __name__ == "__main__":
    main()
