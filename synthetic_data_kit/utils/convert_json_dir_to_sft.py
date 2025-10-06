#!/usr/bin/env python3
"""
convert_json_dir_to_sft.py

Purpose:
- Convert a directory of JSON specs into chat-style JSONL for LLM fine-tuning.
- Produces two tasks: QA (with summary context) and Summarization.
- Validates, deduplicates, and splits into train/val.

Usage:
  python convert_json_dir_to_sft.py --input_dir ./in_json --out_dir ./out_jsonl --val_ratio 0.1 --seed 17

Input JSON schema (per file):
{
  "summary": "<string>",
  "qa_pairs": [{"question":"<string>", "answer":"<string>"}, ...]
}
"""

import argparse, json, hashlib, os, sys, glob, random, re
from collections import defaultdict

def sha1_text(s: str) -> str:
    h = hashlib.sha1()
    h.update(s.encode("utf-8"))
    return h.hexdigest()

def norm_text(s: str) -> str:
    if s is None:
        return ""
    # Normalize whitespace, unify dashes and quotes lightly
    s = s.replace("\r\n","\n").replace("\r","\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s.strip())
    return s

def validate_item(data, fname):
    errors = []
    if not isinstance(data, dict):
        errors.append("root_not_object")
        return False, errors
    if "summary" not in data or not isinstance(data["summary"], str) or not data["summary"].strip():
        errors.append("missing_or_empty_summary")
    if "qa_pairs" not in data or not isinstance(data["qa_pairs"], list) or len(data["qa_pairs"]) == 0:
        errors.append("missing_or_empty_qa_pairs")
    else:
        for i, qa in enumerate(data["qa_pairs"]):
            if not isinstance(qa, dict):
                errors.append(f"qa_{i}_not_object")
                continue
            if "question" not in qa or not isinstance(qa["question"], str) or not qa["question"].strip():
                errors.append(f"qa_{i}_missing_question")
            if "answer" not in qa or not isinstance(qa["answer"], str) or not qa["answer"].strip():
                errors.append(f"qa_{i}_missing_answer")
    return len(errors) == 0, errors

def make_qa_rows(summary, qa_pairs, file_id, filename):
    rows = []
    for idx, qa in enumerate(qa_pairs):
        q = norm_text(qa["question"])
        a = norm_text(qa["answer"])
        if not q or not a:
            continue
        user_content = f"{summary}\n\nQ: {q}"
        source_id = f"{file_id}:{os.path.basename(filename)}#{idx}"
        row = {
            "messages": [
                {"role": "system", "content": "You answer based on the provided context only."},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": a}
            ],
            "source_id": source_id
        }
        rows.append(row)
    return rows

def make_sum_row(summary, file_id, filename, gold_summary=None):
    # gold_summary defaults to the input summary itself for reconstruction training
    out = {
        "messages": [
            {"role": "system", "content": "Summarize concisely the scope and capabilities."},
            {"role": "user", "content": summary},
            {"role": "assistant", "content": gold_summary if gold_summary is not None else summary}
        ],
        "source_id": f"{file_id}:{os.path.basename(filename)}"
    }
    return out

def deterministic_split(keys, val_ratio=0.1, seed=17):
    # Split by filename-hash to avoid leakage
    random.seed(seed)
    shuffled = sorted(keys)  # stable
    random.shuffle(shuffled)
    n_val = max(1, int(len(shuffled) * val_ratio))
    val_set = set(shuffled[:n_val])
    return val_set

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--val_ratio", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()

    in_dir = args.input_dir
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    qa_rows_all = []
    sum_rows_all = []
    errors_log = []
    seen_qa = set()  # dedupe identical (summary, Q, A)

    # ingest
    files = sorted(glob.glob(os.path.join(in_dir, "*.json")))
    if not files:
        print("ERROR: no .json files found in input_dir", file=sys.stderr)
        sys.exit(2)

    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            errors_log.append({"file": fp, "error": f"json_parse_error:{e}"})
            continue

        valid, errs = validate_item(data, fp)
        if not valid:
            errors_log.append({"file": fp, "error": ";".join(errs)})
            continue

        summary = norm_text(data["summary"])
        qa_pairs = [{"question": norm_text(x["question"]), "answer": norm_text(x["answer"])} for x in data["qa_pairs"]]

        file_id = sha1_text(summary + json.dumps(qa_pairs, ensure_ascii=False))
        # QA rows
        for row in make_qa_rows(summary, qa_pairs, file_id, fp):
            sig = sha1_text(row["messages"][1]["content"] + "||" + row["messages"][2]["content"])
            if sig not in seen_qa:
                qa_rows_all.append(row)
                seen_qa.add(sig)

        # Summarization row
        sum_rows_all.append(make_sum_row(summary, file_id, fp, gold_summary=summary))

    # write raw outputs
    qa_path = os.path.join(out_dir, "qa.jsonl")
    sum_path = os.path.join(out_dir, "summarization.jsonl")
    with open(qa_path, "w", encoding="utf-8") as f:
        for r in qa_rows_all:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(sum_path, "w", encoding="utf-8") as f:
        for r in sum_rows_all:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # deterministic split by filename-derived id present in source_id
    # group by base filename to keep all QAs from one file in same split
    file_keys = sorted({r["source_id"].split(":")[1].split("#")[0] for r in qa_rows_all + sum_rows_all})
    val_set = deterministic_split(file_keys, args.val_ratio, args.seed)

    split_dir = os.path.join(out_dir, "split")
    os.makedirs(split_dir, exist_ok=True)

    def write_split(rows, base):
        train_fp = os.path.join(split_dir, f"{base}_train.jsonl")
        val_fp   = os.path.join(split_dir, f"{base}_val.jsonl")
        with open(train_fp, "w", encoding="utf-8") as ft, open(val_fp, "w", encoding="utf-8") as fv:
            for r in rows:
                key = r["source_id"].split(":")[1].split("#")[0]
                if key in val_set:
                    fv.write(json.dumps(r, ensure_ascii=False) + "\n")
                else:
                    ft.write(json.dumps(r, ensure_ascii=False) + "\n")
        return train_fp, val_fp

    qa_train, qa_val = write_split(qa_rows_all, "qa")
    sum_train, sum_val = write_split(sum_rows_all, "sum")

    # errors log
    if errors_log:
        with open(os.path.join(out_dir, "errors.jsonl"), "w", encoding="utf-8") as fe:
            for e in errors_log:
                fe.write(json.dumps(e, ensure_ascii=False) + "\n")

    # stats
    stats = {
        "input_files": len(files),
        "qa_rows": len(qa_rows_all),
        "summarization_rows": len(sum_rows_all),
        "val_ratio": args.val_ratio,
        "seed": args.seed,
        "qa_train_path": qa_train,
        "qa_val_path": qa_val,
        "sum_train_path": sum_train,
        "sum_val_path": sum_val,
        "errors_count": len(errors_log)
    }
    with open(os.path.join(out_dir, "stats.json"), "w", encoding="utf-8") as fs:
        json.dump(stats, fs, ensure_ascii=False, indent=2)

    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
#python convert_json_dir_to_sft.py --input_dir "C:\Users\thevermeulen\data\generated\" --out_dir "C:\Users\thevermeulen\data\generated\out_jsonl" --val_ratio 0.1 --seed 17
