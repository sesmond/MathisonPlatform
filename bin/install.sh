#!/usr/bin/env bash
echo "将mathison 项目安装到本地"
python setup.py install
python setup.py clean --all
rm -rf mathison.egg-info dist
