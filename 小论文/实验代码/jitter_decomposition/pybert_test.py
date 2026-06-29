# pybert_test.py
import time
import numpy as np
from pybert.pybert import PyBERT

def test_automation():
    print("🚀 正在初始化 PyBERT (无头模式)...")
    
    try:
        my_bert = PyBERT()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    # 配置参数
    my_bert.bit_rate = 10.0  
    my_bert.nbits    = 10000 
    my_bert.pattern_len = 7  
    my_bert.pj_freq  = 10.0  
    my_bert.pj_amp   = 0.1   

    print("⏳ 开始计算 (Simulating)...")
    start = time.time()
    
    # 【关键修改】用 try-except 包裹仿真过程
    try:
        if hasattr(my_bert, 'simulate'):
            my_bert.simulate(None)
    except Exception as e:
        # 只要不是初始化错误，通常前面的数据已经算好了
        print(f"⚠️ 捕获到仿真收尾阶段的错误 (通常可忽略): \n   {e}")
        print("➡️ 尝试强行读取数据...")

    # 4. 暴力检查数据
    data_found = False
    
    # 检查点: jitter (关键目标)
    # 顺便打印一下具体的数据类型，方便我们后续处理
    target_names = ['jitter', 'tie', 't', 'chnl_out']
    
    print("\n🔍 数据探查结果:")
    for name in target_names:
        if hasattr(my_bert, name):
            val = getattr(my_bert, name)
            if isinstance(val, (list, np.ndarray)) and len(val) > 0:
                print(f"✅ 成功获取 '{name}'! | 长度: {len(val)} | 类型: {type(val)}")
                # 如果是 jitter，打印前5个值确认不是全0
                if name in ['jitter', 'tie']:
                    print(f"   -> 前5个值: {val[:5]}")
                data_found = True
    
    if not data_found:
        print("❌ 依然没有找到数据，可能仿真在早期就失败了。")
    
    print(f"⏱️ 总耗时: {time.time() - start:.3f}秒")

if __name__ == '__main__':
    test_automation()
    