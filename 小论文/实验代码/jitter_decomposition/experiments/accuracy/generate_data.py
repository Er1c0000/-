import os
import multiprocessing
from functools import partial
from tqdm import tqdm
import time
import sys

# Get the absolute path of the current script file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to get the project root directory
project_root = os.path.dirname(os.path.dirname(current_dir))
# Add the project root to the Python path
sys.path.insert(0, project_root)

from core.tie_generate import generate_aligned_dataset

def generator_task(task_params, datasets_dir):
    """
    单个进程执行的任务：生成数据
    task_params: (freq, repeat_idx)
    """
    freq, i = task_params
    
    freq_label = f"{int(freq/1e3)}kHz" if freq < 1e6 else f"{freq/1e6:.1f}MHz"
    seed = 42 + i
    
    try:
        filename = f"tie_data_{freq_label}_rep{i}.csv"
        # 调用生成函数
        generate_aligned_dataset(
            filename=filename, 
            save_dir=datasets_dir, 
            pj_freq=freq,
            seed=seed
        )
        return None
    except Exception as e:
        return f"Error generating {freq_label} Rep {i}: {str(e)}"

def run_data_generation():
    # 实验参数 (需与 experiment_accuracy.py 保持一致)
    frequencies = [10e3, 50e3, 100e3, 500e3, 1e6, 5e6, 10e6]
    repeats = 5
    
    # 路径准备
    output_dir = "datasets/accuracy"
    datasets_dir = os.path.join(output_dir, "datasets")
    if not os.path.exists(datasets_dir):
        os.makedirs(datasets_dir)

    # 构造任务列表
    tasks = [(f, i) for f in frequencies for i in range(repeats)]
    
    print(f"🚀 开始生成实验数据...")
    print(f"📦 待生成文件总数: {len(tasks)}")
    print(f"📂 保存目录: {datasets_dir}")

    start_time = time.time()
    
    # 使用进程池
    num_cpus = max(1, multiprocessing.cpu_count() - 2)
    
    func = partial(generator_task, datasets_dir=datasets_dir)
    
    with multiprocessing.Pool(processes=num_cpus) as pool:
        for res in tqdm(pool.imap_unordered(func, tasks), total=len(tasks), desc="生成进度"):
            if res:
                print(f"\n❌ {res}")

    duration = time.time() - start_time
    print(f"\n✅ 数据生成完成! 总耗时: {duration:.2f} 秒")

if __name__ == "__main__":
    run_data_generation()
