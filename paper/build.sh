#!/bin/bash

# 检查是否有debug参数
if [[ "$1" == "debug" ]]; then
	DEBUG=true
else
	DEBUG=false
fi

# 创建 build 目录（如果不存在）
mkdir -p build
mkdir -p build/chapters

# 完整编译流程
if [[ "$DEBUG" == "true" ]]; then
	# Debug模式：显示所有输出
	echo "Running in debug mode - showing all output"
	xelatex -output-directory=build main
	bibtex build/main
	xelatex -output-directory=build main
	xelatex -output-directory=build main
else
	# 正常模式：仅显示错误和警告
	xelatex -output-directory=build main 2>&1 | rg -i "error|warning"
	bibtex build/main 2>&1 | rg -i "error|warning"
	xelatex -output-directory=build main 2>&1 | rg -i "error|warning"
	xelatex -output-directory=build main 2>&1 | rg -i "error|warning"
fi

# 可选：添加成功提示
echo "Compilation completed. Output files are in ./build/"
