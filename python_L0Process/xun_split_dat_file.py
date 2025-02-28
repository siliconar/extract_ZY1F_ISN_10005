import os
from Utils import *

def split_dat_file(input_file, frames_per_file, output_dir):
    """
    从输入的 dat 文件中，每读取 frames_per_file 帧图像数据，
    就保存为一个新的输出文件到 output_dir 目录。

    每帧图像数据大小：2048*2*76 字节 = 311296 字节。

    参数：
      input_file: 输入的 dat 文件路径
      frames_per_file: 每个输出文件包含的帧数
      output_dir: 输出文件保存的目录
    """
    frame_size = 2048 * 2 * 76  # 每帧大小，311296字节

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_index = 1  # 用于输出文件命名
    frame_count = 0  # 当前输出文件中已写入的帧数
    out_file = None

    with open(input_file, 'rb') as fin:
        while True:
            frame = fin.read(frame_size)
            # 当读取不到完整的一帧时，退出循环
            if not frame or len(frame) < frame_size:
                break

            # 如果当前输出文件还未打开或已达到 N 帧，打开一个新文件
            if frame_count % frames_per_file == 0:
                # 关闭上一个文件
                if out_file:
                    out_file.close()
                    # 同时写入hdr
                    hdr_filename = change_file_extension(output_filename, "", ".hdr")
                    generate_envi_hdr(2048, frame_count, 76, "BIL", hdr_filename)

                output_filename = os.path.join(output_dir, f"output_{file_index:03d}.bin")
                out_file = open(output_filename, 'wb')
                file_index += 1
                frame_count = 0

            # 将当前帧写入输出文件
            out_file.write(frame)
            frame_count += 1

    # 关闭最后一个输出文件
    if out_file:
        out_file.close()


# 示例调用
if __name__ == '__main__':
    input_file = "E:/解压缩linshi/all_image.dat"  # 输入的 dat 文件
    frames_per_file = 3000  # 每个输出文件包含10帧图像数据
    output_dir = "E:/解压缩linshi/split_image/"  # 输出目录
    split_dat_file(input_file, frames_per_file, output_dir)
