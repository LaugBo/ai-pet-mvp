# 心情图片管理器
# 功能：管理AI宠物的心情表情图片

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

class ImageType(Enum):
    """图片类型"""
    STATIC = "static"      # 静态图片
    ANIMATED = "animated"  # 动态图片
    SPECIAL = "special"    # 特殊图片

class MoodImageManager:
    """
    心情图片管理器
    管理AI宠物的心情表情图片
    """
    
    def __init__(self, assets_path: str = None):
        """
        初始化心情图片管理器
        
        参数:
            assets_path: 资源文件路径
        """
        if assets_path is None:
            # 默认路径
            current_dir = Path(__file__).parent.parent.parent.parent
            self.assets_path = current_dir / "src" / "ui" / "assets" / "moods"
        else:
            self.assets_path = Path(assets_path)
        
        # 确保目录存在
        self._ensure_directories()
        
        # 图片缓存
        self.image_cache = {}
        
        # 图片配置
        self.image_config = {
            "default_sizes": {
                "small": (64, 64),
                "medium": (128, 128),
                "large": (256, 256)
            },
            "supported_formats": [".png", ".jpg", ".jpeg", ".gif"],
            "fallback_images": {
                "happy": "default_happy.png",
                "excited": "default_excited.png",
                "sad": "default_sad.png",
                "proud": "default_proud.png",
                "confused": "default_confused.png",
                "neutral": "default_neutral.png"
            }
        }
        
        # 扫描图片
        self._scan_images()
        
        print(f"心情图片管理器初始化完成")
        print(f"资源路径: {self.assets_path}")
        print(f"发现 {len(self.available_moods)} 种心情的图片")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 创建基础心情目录
        mood_dirs = ["happy", "excited", "sad", "proud", "confused", "neutral"]
        for mood_dir in mood_dirs:
            (self.assets_path / mood_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建特殊目录
        special_dirs = ["special", "animated", "temp"]
        for special_dir in special_dirs:
            (self.assets_path / special_dir).mkdir(parents=True, exist_ok=True)
    
    def _scan_images(self):
        """扫描可用图片"""
        self.available_images = {}
        self.available_moods = set()
        
        # 扫描所有心情目录
        for mood_dir in self.assets_path.iterdir():
            if not mood_dir.is_dir():
                continue
            
            mood_name = mood_dir.name
            if mood_name.startswith(".") or mood_name in ["special", "animated", "temp"]:
                continue
            
            # 扫描该心情目录下的图片
            mood_images = []
            for image_file in mood_dir.iterdir():
                if image_file.suffix.lower() in self.image_config["supported_formats"]:
                    mood_images.append({
                        "path": str(image_file),
                        "name": image_file.name,
                        "size": image_file.stat().st_size,
                        "type": ImageType.STATIC.value
                    })
            
            if mood_images:
                self.available_images[mood_name] = mood_images
                self.available_moods.add(mood_name)
                print(f"  ✅ {mood_name}: {len(mood_images)} 张图片")
    
    def get_mood_image(self, mood_name: str, size: str = "medium", variant: int = 0) -> Optional[str]:
        """
        获取指定心情的图片路径
        
        参数:
            mood_name: 心情名称
            size: 图片大小 ("small", "medium", "large")
            variant: 图片变体编号
            
        返回:
            图片路径，如果不存在则返回None
        """
        # 检查心情是否有可用图片
        if mood_name not in self.available_images or not self.available_images[mood_name]:
            # 使用备用图片
            fallback = self.image_config["fallback_images"].get(mood_name)
            if fallback:
                fallback_path = self.assets_path / "default" / fallback
                if fallback_path.exists():
                    return str(fallback_path)
            return None
        
        # 获取可用的图片列表
        mood_images = self.available_images[mood_name]
        
        # 确保variant在有效范围内
        variant = variant % len(mood_images)
        
        return mood_images[variant]["path"]
    
    def get_random_mood_image(self, mood_name: str, size: str = "medium") -> Optional[str]:
        """
        获取指定心情的随机图片
        
        参数:
            mood_name: 心情名称
            size: 图片大小
            
        返回:
            图片路径
        """
        if mood_name not in self.available_images or not self.available_images[mood_name]:
            return self.get_mood_image(mood_name, size)
        
        mood_images = self.available_images[mood_name]
        random_image = random.choice(mood_images)
        
        return random_image["path"]
    
    def get_all_mood_images(self, mood_name: str) -> List[Dict[str, any]]:
        """
        获取指定心情的所有图片
        
        参数:
            mood_name: 心情名称
            
        返回:
            图片信息列表
        """
        return self.available_images.get(mood_name, [])
    
    def get_mood_image_count(self, mood_name: str) -> int:
        """
        获取指定心情的图片数量
        
        参数:
            mood_name: 心情名称
            
        返回:
            图片数量
        """
        return len(self.available_images.get(mood_name, []))
    
    def get_available_moods(self) -> List[str]:
        """
        获取有可用图片的心情列表
        
        返回:
            心情列表
        """
        return list(self.available_moods)
    
    def add_image(self, mood_name: str, image_path: str, image_type: ImageType = ImageType.STATIC) -> bool:
        """
        添加新图片
        
        参数:
            mood_name: 心情名称
            image_path: 原图片路径
            image_type: 图片类型
            
        返回:
            是否添加成功
        """
        try:
            # 确保心情目录存在
            mood_dir = self.assets_path / mood_name
            mood_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成新文件名
            from pathlib import Path
            source_path = Path(image_path)
            if not source_path.exists():
                print(f"❌ 源文件不存在: {image_path}")
                return False
            
            # 检查文件格式
            if source_path.suffix.lower() not in self.image_config["supported_formats"]:
                print(f"❌ 不支持的图片格式: {source_path.suffix}")
                return False
            
            # 生成唯一文件名
            timestamp = int(time.time())
            new_filename = f"{mood_name}_{timestamp}{source_path.suffix}"
            dest_path = mood_dir / new_filename
            
            # 复制文件
            import shutil
            shutil.copy2(source_path, dest_path)
            
            # 添加到缓存
            if mood_name not in self.available_images:
                self.available_images[mood_name] = []
                self.available_moods.add(mood_name)
            
            image_info = {
                "path": str(dest_path),
                "name": new_filename,
                "size": dest_path.stat().st_size,
                "type": image_type.value
            }
            
            self.available_images[mood_name].append(image_info)
            
            print(f"✅ 图片添加成功: {mood_name}/{new_filename}")
            return True
            
        except Exception as e:
            print(f"❌ 添加图片失败: {e}")
            return False
    
    def remove_image(self, mood_name: str, image_name: str) -> bool:
        """
        移除图片
        
        参数:
            mood_name: 心情名称
            image_name: 图片文件名
            
        返回:
            是否移除成功
        """
        try:
            image_path = self.assets_path / mood_name / image_name
            
            if not image_path.exists():
                print(f"❌ 图片不存在: {image_path}")
                return False
            
            # 删除文件
            image_path.unlink()
            
            # 从缓存中移除
            if mood_name in self.available_images:
                self.available_images[mood_name] = [
                    img for img in self.available_images[mood_name]
                    if img["name"] != image_name
                ]
                
                # 如果没有图片了，从可用心情中移除
                if not self.available_images[mood_name]:
                    del self.available_images[mood_name]
                    self.available_moods.discard(mood_name)
            
            print(f"✅ 图片移除成功: {mood_name}/{image_name}")
            return True
            
        except Exception as e:
            print(f"❌ 移除图片失败: {e}")
            return False
    
    def get_image_info(self, image_path: str) -> Optional[Dict[str, any]]:
        """
        获取图片信息
        
        参数:
            image_path: 图片路径
            
        返回:
            图片信息
        """
        try:
            from pathlib import Path
            path = Path(image_path)
            
            if not path.exists():
                return None
            
            return {
                "path": str(path),
                "name": path.name,
                "size": path.stat().st_size,
                "created": path.stat().st_ctime,
                "modified": path.stat().st_mtime,
                "extension": path.suffix.lower()
            }
            
        except Exception as e:
            print(f"❌ 获取图片信息失败: {e}")
            return None
    
    def get_images_by_type(self, image_type: ImageType) -> List[Dict[str, any]]:
        """
        按类型获取图片
        
        参数:
            image_type: 图片类型
            
        返回:
            图片列表
        """
        all_images = []
        for mood_name, images in self.available_images.items():
            for image in images:
                if image["type"] == image_type.value:
                    all_images.append({
                        "mood": mood_name,
                        **image
                    })
        
        return all_images
    
    def get_total_image_count(self) -> int:
        """获取图片总数"""
        total = 0
        for images in self.available_images.values():
            total += len(images)
        return total
    
    def get_storage_info(self) -> Dict[str, any]:
        """获取存储信息"""
        total_size = 0
        mood_counts = {}
        
        for mood_name, images in self.available_images.items():
            mood_size = sum(img["size"] for img in images)
            total_size += mood_size
            mood_counts[mood_name] = {
                "count": len(images),
                "size": mood_size
            }
        
        # 转换为人类可读格式
        def human_readable_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        
        return {
            "total_images": self.get_total_image_count(),
            "total_size": human_readable_size(total_size),
            "total_size_bytes": total_size,
            "mood_counts": mood_counts,
            "available_moods": len(self.available_moods)
        }

# 使用示例
if __name__ == "__main__":
    print("心情图片管理器测试")
    print("=" * 50)
    
    import time
    import tempfile
    
    # 创建管理器
    manager = MoodImageManager()
    
    # 获取可用心情
    print("可用心情:", manager.get_available_moods())
    
    # 测试获取图片
    test_moods = ["happy", "sad", "excited"]
    for mood in test_moods:
        print(f"\n测试心情: {mood}")
        image_path = manager.get_mood_image(mood)
        if image_path:
            print(f"  图片路径: {image_path}")
            print(f"  图片数量: {manager.get_mood_image_count(mood)}")
        else:
            print(f"  ⚠️ 无可用图片")
    
    # 测试随机图片
    print("\n测试随机图片:")
    for mood in test_moods:
        random_image = manager.get_random_mood_image(mood)
        if random_image:
            print(f"  {mood}: {random_image}")
    
    # 获取存储信息
    print("\n存储信息:")
    storage_info = manager.get_storage_info()
    for key, value in storage_info.items():
        if key != "mood_counts":
            print(f"  {key}: {value}")
    
    print("=" * 50)
    print("心情图片管理器测试完成")