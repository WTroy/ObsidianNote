#!/usr/bin/env python3
"""运行关联分析并输出到文件"""
import sys
import io

# 将输出重定向到文件和终端
log_file = open("/tmp/link_analysis.log", "w", encoding="utf-8")

class Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()
    def flush(self):
        for s in self.streams:
            s.flush()

sys.stdout = Tee(sys.__stdout__, log_file)
sys.stderr = Tee(sys.__stderr__, log_file)

from import_youdao import analyze_links
analyze_links(dry_run=False)
log_file.close()
