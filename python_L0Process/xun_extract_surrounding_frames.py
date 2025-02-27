import os


## 用于解压后数据，提取某一帧的前10帧或后10帧
def extract_surrounding_frames_flexible(input_file, output_file):
    """
    处理由多帧数据组成的二进制文件，每帧理论上为314380字节，
      - 前3084字节为辅助数据
      - 后311296字节为图像数据
    文件中可能丢帧，所以每次都搜索帧头。

    帧头信息：
      - 每帧开头至少应为 09 15 c0 00（4字节）
      - 目标帧的前12字节为：09 15 c0 00 08 00 26 0c 00 01 a1 a1

    找到目标帧后，输出：
      1. 目标帧前10帧的图像数据（如果不足则输出已有帧，并提示）
      2. 目标帧的图像数据
      3. 目标帧后10帧的图像数据
    """
    frame_size = 314380  # 每帧总字节数
    aux_size = 3084  # 辅助数据部分字节数
    image_size = 311296  # 图像数据部分字节数

    # 定义基本帧头和目标帧头（前12字节）
    basic_header = b'\x09\x15\xc0\x00'
    target_header = b'\x09\x15\xc0\x00\x08\x00\x26\x0c\x00\x01\xa1\xa1'

    chunk_size = 4096  # 每次读取的块大小
    buffer = b''  # 用于存放未处理的数据
    file_offset = 0  # 当前文件的绝对偏移量（与buffer相关）
    frames = []  # 存储所有帧头信息，元组：(帧头起始绝对偏移, 是否为目标帧)

    # 第一阶段：扫描整个文件，记录所有帧头位置
    with open(input_file, 'rb') as fin:
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            buffer += chunk
            search_pos = 0
            # 在buffer中搜索基本帧头（4字节）
            while True:
                idx = buffer.find(basic_header, search_pos)
                if idx == -1:
                    break
                # 若buffer中剩余不足12字节，则等待下次补足后再判断是否为目标帧
                if len(buffer) - idx < 12:
                    break
                # 判断是否为目标帧：比较前12字节
                is_target = (buffer[idx:idx + 12] == target_header)
                # 计算该帧头的绝对位置：当前文件已读取总字节 file_offset，
                # 减去当前buffer长度，再加上当前索引
                abs_offset = file_offset - len(buffer) + idx
                frames.append((abs_offset, is_target))
                # 继续向后查找下一个匹配
                search_pos = idx + 1
            # 为防止帧头跨块丢失，保留buffer末尾最多11字节（12-1）
            keep = 11
            if len(buffer) > keep:
                buffer = buffer[-keep:]
            file_offset += len(chunk)

    # 检查是否找到目标帧
    target_index = None
    for i, (_, is_target) in enumerate(frames):
        if is_target:
            target_index = i
            break
    if target_index is None:
        print("未找到目标帧！")
        return

    print(f"目标帧在第 {target_index + 1} 个记录处，共找到 {len(frames)} 帧。")

    # 计算需要输出的帧范围：目标帧前10帧、目标帧、目标帧后10帧
    start_index = max(0, target_index - 30)
    end_index = min(len(frames) - 1, target_index + 200)

    # 第二阶段：利用记录的帧头偏移，依次读取每一帧数据中的图像部分
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        for i in range(start_index, end_index + 1):
            frame_offset, _ = frames[i]
            fin.seek(frame_offset)
            frame_data = fin.read(frame_size)
            if len(frame_data) < frame_size:
                print(f"帧 {i + 1} 数据不足，跳过。")
                continue
            # 截取图像数据部分（辅助数据后）
            image_data = frame_data[aux_size: aux_size + image_size]
            fout.write(image_data)
    print(f"输出帧范围：{start_index + 1} 至 {end_index + 1} 共 {end_index - start_index + 1} 帧图像数据。")


# 示例调用
if __name__ == '__main__':
    input_file = "E:/解压缩linshi/tmp_20250227_115137413_0.dat"
    output_file = "E:/解压缩linshi/image_10_10.dat"
    extract_surrounding_frames_flexible(input_file, output_file)