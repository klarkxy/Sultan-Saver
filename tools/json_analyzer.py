import ijson
import os
from collections import defaultdict
from datetime import datetime


def analyze_large_json(input_path, output_dir):
    """
    分析大型JSON文件并生成文档

    参数:
        input_path: 输入JSON文件路径
        output_dir: 输出文档目录
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 初始化分析数据结构
    analysis = {
        "file_info": {
            "filename": os.path.basename(input_path),
            "size": os.path.getsize(input_path),
            "last_modified": datetime.fromtimestamp(
                os.path.getmtime(input_path)
            ).isoformat(),
            "analysis_date": datetime.now().isoformat(),
        },
        "structure": defaultdict(int),
        "key_stats": defaultdict(int),
        "value_types": defaultdict(int),
        "array_lengths": defaultdict(int),
    }

    try:
        with open(input_path, "rb") as f:
            # 使用ijson解析大型JSON文件
            parser = ijson.parse(f)

            for prefix, event, value in parser:
                # 记录结构信息
                analysis["structure"][f"{prefix} {event}"] += 1

                # 记录键名统计
                if event == "map_key":
                    analysis["key_stats"][value] += 1

                # 记录值类型统计
                if event in ["string", "number", "boolean", "null"]:
                    analysis["value_types"][event] += 1

                # 记录数组长度
                if event == "start_array":
                    array_length = 0
                    for _, ev, _ in parser:
                        if ev == "end_array":
                            break
                        array_length += 1
                    analysis["array_lengths"][array_length] += 1

        # 生成文档
        doc_path = os.path.join(
            output_dir, f"{analysis['file_info']['filename']}_analysis.txt"
        )
        with open(doc_path, "w", encoding="utf-8") as doc:
            doc.write(f"JSON文件分析报告\n{'='*30}\n\n")
            doc.write(f"文件信息:\n{'-'*20}\n")
            for k, v in analysis["file_info"].items():
                doc.write(f"{k}: {v}\n")

            doc.write(f"\n结构分析:\n{'-'*20}\n")
            for k, v in sorted(
                analysis["structure"].items(), key=lambda x: x[1], reverse=True
            ):
                doc.write(f"{k}: {v}\n")

            doc.write(f"\n键名统计 (前20):\n{'-'*20}\n")
            for k, v in sorted(
                analysis["key_stats"].items(), key=lambda x: x[1], reverse=True
            )[:20]:
                doc.write(f"{k}: {v}\n")

            doc.write(f"\n值类型统计:\n{'-'*20}\n")
            for k, v in sorted(
                analysis["value_types"].items(), key=lambda x: x[1], reverse=True
            ):
                doc.write(f"{k}: {v}\n")

            doc.write(f"\n数组长度统计:\n{'-'*20}\n")
            for k, v in sorted(analysis["array_lengths"].items(), key=lambda x: x[0]):
                doc.write(f"长度 {k}: {v} 个数组\n")

        print(f"分析完成，文档已保存到: {doc_path}")
        return True

    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("用法: python json_analyzer.py <input_json> <output_dir>")
        sys.exit(1)

    analyze_large_json(sys.argv[1], sys.argv[2])
