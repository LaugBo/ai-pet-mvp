#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本 - 完整版本
支持多种测试模式、覆盖率报告和并行测试
"""

import os
import sys
import argparse
import subprocess
import platform
import json
import time
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger, setup_logging
from src.utils.helpers import Timer, format_size, format_time
from src.utils.error_handler import safe_call, ErrorHandler


class TestRunner:
    """完整的测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.coverage_dir = self.project_root / "htmlcov"
        
        # 设置日志
        self.logger = setup_logging("test_runner", "INFO")
        self.error_handler = ErrorHandler(self.logger)
        
        # 支持的测试类型
        self.test_types = {
            "all": ("运行所有测试", ["tests/"]),
            "core": ("运行核心模块测试", ["tests/test_core/"]),
            "ui": ("运行UI模块测试", ["tests/test_ui/"]),
            "utils": ("运行工具模块测试", ["tests/test_utils/"]),
            "integration": ("运行集成测试", ["tests/test_integration/"]),
            "unit": ("运行单元测试（不含UI）", ["tests/test_core/", "tests/test_utils/"]),
            "quick": ("快速测试（不含UI和集成）", ["tests/test_core/", "tests/test_utils/"]),
            "smoke": ("冒烟测试", ["tests/test_integration/test_full_app.py"]),
            "performance": ("性能测试", ["tests/test_integration/test_full_app.py::TestPerformance"])
        }
        
        # 测试配置文件
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载测试配置"""
        config_path = self.project_root / "tests" / "test_config.json"
        default_config = {
            "default_test_type": "all",
            "coverage_threshold": 80.0,
            "timeout": 300,  # 5分钟
            "parallel_workers": "auto",
            "html_report": True,
            "xml_report": False,
            "verbose_output": True,
            "fail_fast": False,
            "markers": {
                "slow": "跳过慢测试",
                "ui": "UI相关测试",
                "integration": "集成测试",
                "performance": "性能测试"
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                return {**default_config, **user_config}
            except Exception as e:
                self.logger.warning(f"加载测试配置失败，使用默认配置: {e}")
        
        return default_config
    
    @safe_call(operation="运行测试")
    def run_tests(self, 
                 test_type: str = "all",
                 coverage: bool = False,
                 verbose: bool = False,
                 parallel: bool = False,
                 failfast: bool = False,
                 markers: List[str] = None,
                 timeout: int = None) -> Dict[str, Any]:
        """
        运行测试
        
        Args:
            test_type: 测试类型
            coverage: 是否生成覆盖率报告
            verbose: 是否显示详细输出
            parallel: 是否并行运行
            failfast: 遇到失败立即停止
            markers: 测试标记筛选
            timeout: 超时时间(秒)
        
        Returns:
            测试结果字典
        """
        self.logger.info("=" * 60)
        self.logger.info(f"🚀 开始运行测试: {test_type}")
        self.logger.info("=" * 60)
        
        # 记录开始时间
        start_time = time.time()
        
        # 构建pytest命令
        cmd = self._build_pytest_command(
            test_type=test_type,
            coverage=coverage,
            verbose=verbose,
            parallel=parallel,
            failfast=failfast,
            markers=markers,
            timeout=timeout
        )
        
        if not cmd:
            self.logger.error(f"不支持的测试类型: {test_type}")
            return {
                "success": False,
                "message": f"不支持的测试类型: {test_type}",
                "elapsed": 0
            }
        
        # 创建报告目录
        self.reports_dir.mkdir(exist_ok=True)
        
        # 运行测试
        result = self._run_pytest_command(cmd)
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        # 处理结果
        test_result = self._process_test_result(result, elapsed, coverage)
        
        # 生成报告
        if test_result["success"]:
            self._generate_test_report(test_result)
        
        return test_result
    
    def _build_pytest_command(self,
                             test_type: str,
                             coverage: bool,
                             verbose: bool,
                             parallel: bool,
                             failfast: bool,
                             markers: List[str],
                             timeout: int) -> List[str]:
        """构建pytest命令"""
        cmd = [sys.executable, "-m", "pytest"]
        
        # 添加测试路径
        if test_type in self.test_types:
            _, paths = self.test_types[test_type]
            cmd.extend(paths)
        elif test_type == "single":
            # 单个测试文件模式
            pass
        else:
            return []
        
        # 基本参数
        cmd.append("--tb=short")  # 简化的回溯信息
        
        if verbose or self.config.get("verbose_output", True):
            cmd.append("-v")
        
        if failfast or self.config.get("fail_fast", False):
            cmd.append("-x")
        
        # 超时设置
        timeout = timeout or self.config.get("timeout", 300)
        cmd.extend(["--timeout", str(timeout)])
        
        # 标记筛选
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        # 覆盖率
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=term",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
                f"--cov-fail-under={self.config.get('coverage_threshold', 80.0)}"
            ])
        
        # 并行测试
        if parallel:
            workers = self.config.get("parallel_workers", "auto")
            cmd.extend(["-n", str(workers)])
        
        # 报告输出
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.config.get("html_report", True):
            html_report = self.reports_dir / f"report_{timestamp}.html"
            cmd.extend(["--html", str(html_report), "--self-contained-html"])
        
        if self.config.get("xml_report", False):
            xml_report = self.reports_dir / f"junit_{timestamp}.xml"
            cmd.extend(["--junit-xml", str(xml_report)])
        
        # 添加项目根目录到Python路径
        cmd.extend(["--import-mode=append"])
        
        return cmd
    
    def _run_pytest_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """运行pytest命令"""
        self.logger.info(f"执行命令: {' '.join(cmd)}")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root) + os.pathsep + env.get("PYTHONPATH", "")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True,
                encoding='utf-8',
                env=env
            )
            return result
        except Exception as e:
            self.logger.error(f"运行测试命令失败: {e}")
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr=str(e)
            )
    
    def _process_test_result(self, 
                           result: subprocess.CompletedProcess, 
                           elapsed: float,
                           coverage: bool) -> Dict[str, Any]:
        """处理测试结果"""
        success = result.returncode == 0
        
        test_result = {
            "success": success,
            "returncode": result.returncode,
            "elapsed": elapsed,
            "elapsed_formatted": format_time(elapsed),
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.logger.info("✅ 所有测试通过！")
            
            if coverage:
                # 显示覆盖率报告
                coverage_data = self._get_coverage_data()
                if coverage_data:
                    test_result["coverage"] = coverage_data
                    self._log_coverage_summary(coverage_data)
                
                # 在浏览器中打开覆盖率报告
                self._open_coverage_report()
        else:
            self.logger.error("❌ 测试失败")
        
        return test_result
    
    def _get_coverage_data(self) -> Optional[Dict[str, Any]]:
        """获取覆盖率数据"""
        coverage_file = self.project_root / "coverage.xml"
        
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                coverage_data = {
                    "lines_covered": 0,
                    "lines_valid": 0,
                    "branch_covered": 0,
                    "branch_valid": 0,
                    "coverage_percentage": 0.0
                }
                
                for metrics in root.findall(".//coverage"):
                    coverage_data["lines_covered"] = int(metrics.get("lines-covered", 0))
                    coverage_data["lines_valid"] = int(metrics.get("lines-valid", 0))
                    coverage_data["branch_covered"] = int(metrics.get("branches-covered", 0))
                    coverage_data["branch_valid"] = int(metrics.get("branches-valid", 0))
                    
                    if coverage_data["lines_valid"] > 0:
                        coverage_data["coverage_percentage"] = (
                            coverage_data["lines_covered"] / coverage_data["lines_valid"] * 100
                        )
                
                return coverage_data
            except Exception as e:
                self.logger.warning(f"解析覆盖率数据失败: {e}")
        
        return None
    
    def _log_coverage_summary(self, coverage_data: Dict[str, Any]):
        """记录覆盖率摘要"""
        self.logger.info("📊 测试覆盖率报告:")
        self.logger.info("=" * 40)
        
        lines_percent = (coverage_data["lines_covered"] / coverage_data["lines_valid"] * 100 
                         if coverage_data["lines_valid"] > 0 else 0)
        branch_percent = (coverage_data["branch_covered"] / coverage_data["branch_valid"] * 100 
                          if coverage_data["branch_valid"] > 0 else 0)
        
        self.logger.info(f"行覆盖率: {lines_percent:.1f}% "
                       f"({coverage_data['lines_covered']}/{coverage_data['lines_valid']})")
        
        if coverage_data["branch_valid"] > 0:
            self.logger.info(f"分支覆盖率: {branch_percent:.1f}% "
                           f"({coverage_data['branch_covered']}/{coverage_data['branch_valid']})")
        
        threshold = self.config.get("coverage_threshold", 80.0)
        if lines_percent >= threshold:
            self.logger.info(f"✅ 达到覆盖率目标 ({threshold}%)")
        else:
            self.logger.warning(f"⚠️  未达到覆盖率目标 ({threshold}%)")
    
    def _open_coverage_report(self):
        """在浏览器中打开覆盖率报告"""
        index_file = self.coverage_dir / "index.html"
        
        if index_file.exists():
            self.logger.info(f"📊 覆盖率报告: file://{index_file}")
            
            # 尝试在浏览器中打开
            try:
                if platform.system() == "Windows":
                    os.startfile(index_file)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(index_file)])
                elif platform.system() == "Linux":
                    subprocess.run(["xdg-open", str(index_file)])
            except Exception as e:
                self.logger.debug(f"无法打开浏览器: {e}")
    
    def _generate_test_report(self, test_result: Dict[str, Any]):
        """生成测试报告"""
        report_file = self.reports_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(test_result, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📄 测试报告已保存: {report_file}")
        except Exception as e:
            self.logger.warning(f"保存测试报告失败: {e}")
    
    def run_single_test(self, 
                       test_path: str, 
                       verbose: bool = False,
                       markers: List[str] = None) -> Dict[str, Any]:
        """运行单个测试"""
        full_path = self.test_dir / test_path
        
        if not full_path.exists():
            return {
                "success": False,
                "message": f"测试文件不存在: {test_path}",
                "elapsed": 0
            }
        
        self.logger.info(f"运行单个测试: {test_path}")
        
        cmd = [sys.executable, "-m", "pytest", str(full_path)]
        
        if verbose:
            cmd.append("-v")
        
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
        
        start_time = time.time()
        result = self._run_pytest_command(cmd)
        elapsed = time.time() - start_time
        
        test_result = {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "elapsed": elapsed,
            "elapsed_formatted": format_time(elapsed),
            "test_path": test_path
        }
        
        if test_result["success"]:
            self.logger.info(f"✅ 测试通过: {test_path}")
        else:
            self.logger.error(f"❌ 测试失败: {test_path}")
        
        return test_result
    
    def list_test_cases(self, detailed: bool = False):
        """列出所有测试用例"""
        self.logger.info("📋 测试用例列表")
        self.logger.info("=" * 60)
        
        # 列出测试类型
        self.logger.info("测试类型:")
        for test_type, (description, _) in self.test_types.items():
            self.logger.info(f"  {test_type:12} - {description}")
        
        # 列出测试文件
        if detailed:
            self.logger.info("\n📁 测试文件:")
            self.logger.info("=" * 40)
            
            test_files = []
            for root, dirs, files in os.walk(self.test_dir):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        rel_path = Path(root).relative_to(self.test_dir) / file
                        test_files.append(str(rel_path))
            
            test_files.sort()
            for test_file in test_files:
                self.logger.info(f"  {test_file}")
                
                # 列出测试函数
                if detailed:
                    test_module = test_file.replace('.py', '').replace('/', '.')
                    try:
                        module = __import__(f"tests.{test_module}", fromlist=['*'])
                        
                        for name in dir(module):
                            if name.startswith("test_"):
                                self.logger.info(f"    - {name}")
                    except:
                        pass
    
    def run_test_suite(self, 
                      suite_type: str = "full",
                      generate_report: bool = True) -> bool:
        """
        运行测试套件
        
        Args:
            suite_type: 套件类型 (full, smoke, ci)
            generate_report: 是否生成报告
        
        Returns:
            是否全部通过
        """
        self.logger.info(f"🔧 运行测试套件: {suite_type}")
        self.logger.info("=" * 60)
        
        suites = {
            "full": [
                ("单元测试", "unit", True, True),
                ("集成测试", "integration", False, True),
                ("覆盖率测试", "all", True, False)
            ],
            "smoke": [
                ("冒烟测试", "smoke", False, False)
            ],
            "ci": [
                ("单元测试", "unit", True, True),
                ("集成测试", "integration", False, False),
                ("覆盖率检查", "all", True, True)
            ],
            "quick": [
                ("快速测试", "quick", False, True)
            ]
        }
        
        if suite_type not in suites:
            self.logger.error(f"不支持的套件类型: {suite_type}")
            return False
        
        suite_config = suites[suite_type]
        all_passed = True
        suite_results = []
        
        # 1. 清理
        self.clean_test_data()
        
        for i, (suite_name, test_type, failfast, coverage) in enumerate(suite_config, 1):
            self.logger.info(f"\n{i}. {suite_name}...")
            
            result = self.run_tests(
                test_type=test_type,
                coverage=coverage,
                verbose=True,
                parallel=True,
                failfast=failfast
            )
            
            suite_results.append({
                "suite": suite_name,
                "success": result["success"],
                "elapsed": result["elapsed_formatted"]
            })
            
            if not result["success"]:
                all_passed = False
                if failfast:
                    self.logger.error(f"❌ {suite_name} 失败，停止套件")
                    break
        
        # 2. 生成套件报告
        if generate_report:
            self._generate_suite_report(suite_type, suite_results, all_passed)
        
        # 3. 总结
        self.logger.info("\n" + "=" * 60)
        
        if all_passed:
            self.logger.info("🎉 测试套件执行完成，所有测试通过！")
        else:
            self.logger.error("❌ 测试套件执行完成，有测试失败")
        
        self.logger.info("=" * 60)
        
        for result in suite_results:
            status = "✅" if result["success"] else "❌"
            self.logger.info(f"{status} {result['suite']:12} - {result['elapsed']}")
        
        return all_passed
    
    def _generate_suite_report(self, 
                             suite_type: str, 
                             results: List[Dict[str, Any]],
                             all_passed: bool):
        """生成套件报告"""
        report = {
            "suite_type": suite_type,
            "timestamp": datetime.now().isoformat(),
            "all_passed": all_passed,
            "results": results,
            "system_info": self._get_system_info()
        }
        
        report_file = self.reports_dir / f"suite_{suite_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📄 套件报告已保存: {report_file}")
        except Exception as e:
            self.logger.warning(f"保存套件报告失败: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        import platform
        import psutil
        
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available
        }
        
        return info
    
    def clean_test_data(self):
        """清理测试数据"""
        self.logger.info("🧹 清理测试数据...")
        
        # 清理覆盖率数据
        dirs_to_clean = [
            self.coverage_dir,
            self.reports_dir,
            self.project_root / ".pytest_cache",
            self.project_root / "__pycache__"
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    self.logger.debug(f"删除目录: {dir_path}")
                except Exception as e:
                    self.logger.warning(f"删除目录失败 {dir_path}: {e}")
        
        # 清理覆盖率文件
        files_to_clean = [
            self.project_root / "coverage.xml",
            self.project_root / ".coverage"
        ]
        
        for file_path in files_to_clean:
            if file_path.exists():
                try:
                    file_path.unlink()
                    self.logger.debug(f"删除文件: {file_path}")
                except Exception as e:
                    self.logger.warning(f"删除文件失败 {file_path}: {e}")
        
        # 清理.pyc文件
        pyc_files = list(self.project_root.rglob("*.pyc"))
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
            except:
                pass
        
        if pyc_files:
            self.logger.info(f"删除 {len(pyc_files)} 个.pyc文件")
        
        # 清理__pycache__目录
        cache_dirs = list(self.project_root.rglob("__pycache__"))
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
            except:
                pass
        
        if cache_dirs:
            self.logger.info(f"删除 {len(cache_dirs)} 个__pycache__目录")
        
        self.logger.info("✅ 清理完成")
    
    def check_test_environment(self) -> bool:
        """检查测试环境"""
        self.logger.info("🔍 检查测试环境...")
        
        checks = []
        
        # 1. 检查Python版本
        python_version = sys.version_info
        checks.append({
            "name": "Python版本",
            "required": "3.8+",
            "actual": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "passed": python_version.major == 3 and python_version.minor >= 8
        })
        
        # 2. 检查必要目录
        required_dirs = [
            self.project_root,
            self.test_dir,
            self.project_root / "src",
            self.project_root / "data"
        ]
        
        for dir_path in required_dirs:
            checks.append({
                "name": f"目录存在: {dir_path.name}",
                "required": "存在",
                "actual": "存在" if dir_path.exists() else "不存在",
                "passed": dir_path.exists()
            })
        
        # 3. 检查必要文件
        required_files = [
            self.project_root / "requirements.txt",
            self.project_root / "run_app.py",
            self.test_dir / "conftest.py"
        ]
        
        for file_path in required_files:
            checks.append({
                "name": f"文件存在: {file_path.name}",
                "required": "存在",
                "actual": "存在" if file_path.exists() else "不存在",
                "passed": file_path.exists()
            })
        
        # 4. 检查依赖
        try:
            import pytest
            checks.append({
                "name": "pytest模块",
                "required": "已安装",
                "actual": f"版本 {pytest.__version__}",
                "passed": True
            })
        except ImportError:
            checks.append({
                "name": "pytest模块",
                "required": "已安装",
                "actual": "未安装",
                "passed": False
            })
        
        # 5. 检查虚拟环境
        in_venv = sys.prefix != sys.base_prefix
        checks.append({
            "name": "虚拟环境",
            "required": "建议使用",
            "actual": "使用中" if in_venv else "未使用",
            "passed": True  # 虚拟环境不是必须的
        })
        
        # 输出检查结果
        all_passed = True
        self.logger.info("检查结果:")
        self.logger.info("=" * 40)
        
        for check in checks:
            status = "✅" if check["passed"] else "❌"
            self.logger.info(f"{status} {check['name']:25} "
                           f"{check['actual']:15} (要求: {check['required']})")
            
            if not check["passed"]:
                all_passed = False
        
        if all_passed:
            self.logger.info("✅ 测试环境检查通过")
        else:
            self.logger.warning("⚠️  测试环境检查未通过")
        
        return all_passed


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI宠物MVP测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s run all                    # 运行所有测试
  %(prog)s run core --coverage        # 运行核心测试并生成覆盖率报告
  %(prog)s single test_core/test_ai_adapter.py  # 运行单个测试
  %(prog)s suite full                 # 运行完整测试套件
  %(prog)s list --detailed            # 列出所有测试用例
  %(prog)s clean                      # 清理测试数据
  %(prog)s check                      # 检查测试环境
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 运行测试命令
    run_parser = subparsers.add_parser("run", help="运行测试")
    run_parser.add_argument("type", nargs="?", default="all", 
                          help="测试类型 (all, core, ui, utils, integration, unit, quick, smoke, performance)")
    run_parser.add_argument("--coverage", "-c", action="store_true", help="生成覆盖率报告")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    run_parser.add_argument("--parallel", "-p", action="store_true", help="并行运行")
    run_parser.add_argument("--failfast", "-x", action="store_true", help="遇到失败立即停止")
    run_parser.add_argument("--markers", "-m", nargs="+", help="测试标记筛选")
    run_parser.add_argument("--timeout", "-t", type=int, help="超时时间(秒)")
    
    # 运行单个测试命令
    single_parser = subparsers.add_parser("single", help="运行单个测试")
    single_parser.add_argument("test_path", help="测试文件路径")
    single_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    single_parser.add_argument("--markers", "-m", nargs="+", help="测试标记筛选")
    
    # 列出测试命令
    list_parser = subparsers.add_parser("list", help="列出测试用例")
    list_parser.add_argument("--detailed", "-d", action="store_true", help="详细列表")
    
    # 运行套件命令
    suite_parser = subparsers.add_parser("suite", help="运行测试套件")
    suite_parser.add_argument("type", nargs="?", default="full", 
                            help="套件类型 (full, smoke, ci, quick)")
    suite_parser.add_argument("--no-report", action="store_true", help="不生成报告")
    
    # 清理命令
    clean_parser = subparsers.add_parser("clean", help="清理测试数据")
    
    # 检查命令
    check_parser = subparsers.add_parser("check", help="检查测试环境")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.command == "run":
            result = runner.run_tests(
                test_type=args.type,
                coverage=args.coverage,
                verbose=args.verbose,
                parallel=args.parallel,
                failfast=args.failfast,
                markers=args.markers,
                timeout=args.timeout
            )
            
            if not result["success"]:
                sys.exit(1)
                
        elif args.command == "single":
            result = runner.run_single_test(
                test_path=args.test_path,
                verbose=args.verbose,
                markers=args.markers
            )
            
            if not result["success"]:
                sys.exit(1)
                
        elif args.command == "list":
            runner.list_test_cases(detailed=args.detailed)
            
        elif args.command == "suite":
            success = runner.run_test_suite(
                suite_type=args.type,
                generate_report=not args.no_report
            )
            
            if not success:
                sys.exit(1)
                
        elif args.command == "clean":
            runner.clean_test_data()
            
        elif args.command == "check":
            success = runner.check_test_environment()
            
            if not success:
                sys.exit(1)
                
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        runner.logger.info("测试被用户中断")
        sys.exit(130)
    except Exception as e:
        runner.logger.error(f"测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()