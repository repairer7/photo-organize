import os
import exifread
import datetime
from geopy.geocoders import Nominatim
import time

# ================= 配置区 =================
BASE_PHOTO_DIR = 'YOUR PTHOT DOWNLOAD PATH'
USER_AGENT = "suzhou_env_monitor_v7"
# ==========================================

def convert_to_decimal(coords, ref):
    try:
        d = float(coords[0].num) / coords[0].den
        m = float(coords[1].num) / coords[1].den
        s = float(coords[2].num) / coords[2].den
        res = d + (m / 60.0) + (s / 3600.0)
        return -res if ref in ['S', 'W'] else res
    except:
        return None

def get_pure_district_name(lat, lon):
    try:
        geolocator = Nominatim(user_agent=USER_AGENT)
        location = geolocator.reverse(f"{lat}, {lon}", language='zh-cn', timeout=10)
        if not location:
            return None
        
        display_name = location.raw.get('display_name', '')
        if "苏州" not in display_name:
            return None

        keywords = ["相城区", "吴中区", "虎丘区", "姑苏区", "吴江区", "昆山市", "常熟市", "太仓市", "张家港市", "工业园区"]
        for k in keywords:
            if k in display_name:
                return k 
        return None
    except Exception:
        return None

def run_photo_analysis():
    """
    分析照片并返回区域列表，加入姑苏区数量校验逻辑
    """
    today = datetime.date.today()
    target_path = os.path.join(BASE_PHOTO_DIR, today.strftime('%Y/%m/%d'))

    if not os.path.exists(target_path):
        return []

    # 1. 使用字典统计每个区域出现的次数
    district_counts = {}
    
    # 获取照片和视频文件（兼容 main.py 的下载范围）
    files = [f for f in os.listdir(target_path) if f.lower().endswith(('.jpg', '.jpeg', '.heic', '.mov'))]
    
    for file_name in files:
        file_path = os.path.join(target_path, file_name)
        
        # 视频文件通常不含 EXIF GPS，这里主要解析图片
        if file_name.lower().endswith(('.jpg', '.jpeg', '.heic')):
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                lat = tags.get('GPS GPSLatitude')
                lat_ref = tags.get('GPS GPSLatitudeRef')
                lon = tags.get('GPS GPSLongitude')
                lon_ref = tags.get('GPS GPSLongitudeRef')

                if lat and lon:
                    lat_v = convert_to_decimal(lat.values, lat_ref.printable)
                    lon_v = convert_to_decimal(lon.values, lon_ref.printable)
                    
                    res = get_pure_district_name(lat_v, lon_v)
                    if res:
                        # 计数逻辑
                        district_counts[res] = district_counts.get(res, 0) + 1
                    time.sleep(0.5)

    # 2. 逻辑过滤
    final_districts = []
    for dist, count in district_counts.items():
        if dist == "姑苏区":
            # 只有姑苏区照片 > 2 张才加入
            if count > 2:
                final_districts.append(dist)
        else:
            # 其他区域只要有 1 张就加入
            final_districts.append(dist)

    return sorted(final_districts)

# --- 主程序执行 ---
if __name__ == "__main__":
    districts = run_photo_analysis()
    
    if districts:
        all_areas = "+".join(districts)
        print(f"检测到的所有苏州辖区: {all_areas}")
    else:
        print("未检测到有效苏州辖区照片（或姑苏区数量不足）")