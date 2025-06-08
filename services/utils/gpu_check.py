#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import torch

from utils import Logger


logger = Logger()


def check_gpu_availability():
    # 检查CUDA是否可用
    if torch.cuda.is_available():
        # 获取可用的GPU数量
        gpu_count = torch.cuda.device_count()
        print(f"检测到 {gpu_count} 个可用的 GPU")

        gpu_infos = []
        # 遍历每个GPU并打印详细信息
        for i in range(gpu_count):
            gpu_properties = torch.cuda.get_device_properties(i)
            info = {
                "name": gpu_properties.name,
                "total_memory(MB)": gpu_properties.total_memory / 1024 ** 2,
                "computing_power": f"{gpu_properties.major}.{gpu_properties.minor}",
                "multi_processor_count": gpu_properties.multi_processor_count
            }
            gpu_infos.append(info)

        # 获取当前选择的GPU
        logger.info(f"当前环境的GPU: {gpu_infos}")
        current_device = torch.cuda.current_device()
        logger.info(f"当前使用的GPU: {current_device}")

        return True

    else:
        logger.info("未检测到可用的 GPU")
        print("未检测到可用的 GPU")
        return False
    

def detect_gpu_settings():
        """
        检测GPU设置以确定数据类型和可用的GPU数量。
        
        返回值：
            tuple: (data_type, num_gpus)
            - data_type: 如果GPU支持FP16则为"half"，否则为"bfloat16"
            - num_gpus: 可用的GPU数量
        """

        if not torch.cuda.is_available():
            logger.warning("No GPU detected. Defaulting to CPU settings.")
            return "bfloat16", 0

        # Check for GPU capabilities
        device_count = torch.cuda.device_count()
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"Detected {device_count} GPU(s): {device_name}")

        # Determine data type based on GPU architecture
        if "NVIDIA" in device_name or 'Tesla' in device_name:
            major, _ = torch.cuda.get_device_capability(0)
            if major < 8:  # Turing architecture or newer
                return "half", device_count
            else:
                return "bfloat16", device_count
        else:
            logger.warning("Non-NVIDIA GPU detected. Defaulting to bfloat16.")
            return "half", device_count
