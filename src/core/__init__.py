# core包初始化文件
# 包含核心功能模块

# 这个文件将core目录标记为Python包
# 并导出所有核心模块

# 版本信息
__version__ = "1.0.0"
__author__ = "AI宠物MVP开发团队"
__description__ = "AI宠物核心功能模块"

# 在需要时动态导入子模块
# 这样可以避免循环导入问题

def get_mood_module():
    """获取心情模块"""
    from . import mood
    return mood

def get_memory_module():
    """获取记忆模块"""
    from . import memory
    return memory

def get_ai_module():
    """获取AI模块"""
    from . import ai
    return ai

# 导出主要类
__all__ = [
    'get_mood_module',
    'get_memory_module', 
    'get_ai_module',
    '__version__',
    '__author__',
    '__description__'
]