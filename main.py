import sys
import os
import subprocess

# 确保脚本路径在系统路径中
script_path = 'YOUR PHOTO DOWNLOAD PATH'
if script_path not in sys.path:
    sys.path.append(script_path)

# 导入你的逻辑模块
import geo
import mv

def run_docker_download():
    """
    第一步：调用 Docker 镜像下载最近的照片和视频
    """
    print("☁️  正在启动 iCloud 下载任务...")
    
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", "/opt/icloud/photo:/home/user/iCloud",
        "-v", "/opt/icloud/config:/config",
        "--entrypoint", "/usr/local/bin/icloudpd",
        "boredazfcuk/icloudpd:latest",
            "--username", "YOUR ICLOUD ACCOUNT",
        "--cookie-directory", "/config",
        "--directory", "/home/user/iCloud",
        "--recent", "80",
        "--domain", "cn",
        # --- 新增参数 ---
        "--set-exif-datetime",  # 确保下载后时间戳正确，方便 geo 识别
        # 如果还是不下载 mov，可以尝试显式取消跳过视频（虽然默认是不跳过的，但镜像配置可能不同）
    ]

    try:
        # run 会等待命令执行完成后再继续
        # 去掉了 -it 因为在后台或脚本中运行通常不需要交互式终端
        subprocess.run(docker_cmd, check=True)
        print("✅ 照片下载完成。")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker 下载失败: {e}")
        sys.exit(1) # 如果下载失败，直接退出，不执行后续的清理

def run_workflow():
    print("\n" + "="*40)
    print("🚀 工作照片自动化处理启动")
    print("="*40)

    # 1. 运行 Docker 下载
    run_docker_download()

    # 2. 执行地理位置分析
    print("\n🔍 正在进行地理位置分析...")
    districts = geo.run_photo_analysis()
    print(f"📍 识别到区域: {districts}")

    # 3. 执行文件归档与本地清理
    print("\n📂 正在归档至 NAS 并清理本地缓存...")
    mv.move_and_cleanup(districts)

    print("\n" + "="*40)
    print("✨ 所有任务已成功处理完毕！")
    print("="*40)

if __name__ == "__main__":
    run_workflow()