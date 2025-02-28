
from Utils import *


def xun_extract_image_data(input_file, output_file):
    """
    处理dat文件，理想的文件结构为：
      3084字节辅助数据 + 2048*2*76字节图像数据（即311296字节）
    从文件中查找以 09 15 c0 00 开头的帧头，
    然后跳过3084字节辅助数据，截取后面的311296字节图像数据，
    写入输出文件；继续查找下一个帧头，直到文件结束。
    """
    pattern = b'\x09\x15\xc0\x00'
    aux_size = 3084
    image_size = 2048 * 2 * 76  # 311296 字节
    chunk_size = 320000         # 每次读取块大小
    buffer = b''
    framecnt =0     # 总共获得的帧数

    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while True:
            # 读取新数据，填充缓冲区
            chunk = fin.read(chunk_size)
            if not chunk:
                break  # 文件读取完毕
            buffer += chunk

            while True:
                # 在缓冲区中查找帧头
                idx = buffer.find(pattern)
                if idx == -1:
                    # 未找到帧头，保留末尾 (pattern长度-1) 字节防止跨块匹配
                    keep = len(pattern) - 1
                    if len(buffer) > keep:
                        buffer = buffer[-keep:]
                    break


                # 计算该帧完整数据所需的总长度：从帧头起，
                # 包括辅助数据(aux_size)和图像数据(image_size)
                total_needed = idx + aux_size + image_size
                if len(buffer) < total_needed:
                    # 缓冲区内数据不足，等待后续数据补充
                    break


                # 记录帧数
                framecnt = framecnt+1

                # 提取图像数据部分：帧头之后跳过辅助数据
                start = idx + aux_size
                end = start + image_size
                image_data = buffer[start:end]
                fout.write(image_data)

                # 从缓冲区中移除已处理的数据
                buffer = buffer[end:]
    print("图像数据提取完成。")

    hdr_file = change_file_extension(output_file, "", ".hdr")
    generate_envi_hdr(2048, framecnt, 76, "BIL", hdr_file)

# 示例调用
if __name__ == '__main__':
    xun_extract_image_data("E:/解压缩linshi/tmp_20250227_115137413_0.dat", "E:/解压缩linshi/all_image.dat")
