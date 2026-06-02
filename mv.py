import os
import shutil
import datetime

# ================= 配置区 =================
SOURCE_BASE = 'YOUR PHOTO DOWNLOAD PATH'
TARGET_BASE = 'YOUR PHOTO SAVE PATH'
# 允许的文件后缀（增加 .mov）
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.heic', '.mov', '.mp4')
# ==========================================

def move_and_cleanup(districts):
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d') # 20260514
    
    # 1. 确定文件夹后缀名
    if districts:
        names = [d.replace('市', '').replace('区', '') for d in districts]
        location_name = "".join(names) 
    else:
        location_name = "未知区域"

    # 2. 创建目标文件夹
    folder_name = f"{date_str}{location_name}"
    target_dir = os.path.join(TARGET_BASE, folder_name)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        print(f"📁 已创建文件夹: {target_dir}")
    else:
        print(f"📁 文件夹已存在: {target_dir}")

    # 3. 复制照片和视频到 NAS
    source_dir = os.path.join(SOURCE_BASE, today.strftime('%Y/%m/%d'))
    
    if os.path.exists(source_dir):
        # 修改点：增加对 .mov 等视频格式的筛选
        files = [f for f in os.listdir(source_dir) if f.lower().endswith(ALLOWED_EXTENSIONS)]
        
        if not files:
            print("ℹ️ 今日目录内没有符合格式的照片或视频文件。")
        else:
            for file_name in files:
                shutil.copy2(os.path.join(source_dir, file_name), os.path.join(target_dir, file_name))
            print(f"✅ 已成功备份 {len(files)} 个文件（含照片及视频）到 NAS")
    else:
        print(f"⚠️ 未发现源目录 {source_dir}，跳过复制阶段")

    # 4. 删除 YOUR PHOTO DOWNLOAD PATH 下的所有内容
    print("🧹 正在清理本地缓存...")
    for item in os.listdir(SOURCE_BASE):
        item_path = os.path.join(SOURCE_BASE, item)
        
        # 修改点：清理时也包含视频格式
        if (os.path.isdir(item_path) and item.isdigit()) or \
           (os.path.isfile(item_path) and item.lower().endswith(ALLOWED_EXTENSIONS)):
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"无法删除 {item}: {e}")
    print("✨ 本地环境清理完成")