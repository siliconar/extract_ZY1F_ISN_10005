import struct
import os
from Utils import *

# 用于中心L0数据，提取图像数据，并生成hdr






def extract_image_data(input_file, output_file,Nbans):

    aux_file = change_file_extension(output_file, "",".aux")
    linescnt =0;
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile, open(aux_file, 'wb') as auxfile:
        while True:
            # 读取3092字节的辅助数据
            aux_data = infile.read(3092)
            if not aux_data:
                print("无数据，跳出")
                break  # 如果没有更多数据，退出循环

            auxfile.write(aux_data[0:20])  # aux文件，写入aux的前12个字节
            # 行计数+1
            linescnt = linescnt+1;
            print(linescnt)
            # 读取Nbans数据
            for i in range(Nbans):
                # 读取高光谱图像数据（4108*N字节）
                frame_data = infile.read(4108)
                # 每个波段的头部12字节和图像数据4096字节
                band_header = frame_data[0 * 4108:0 * 4108 + 12]  # 获取波段头部
                band_data = frame_data[0 * 4108 + 12:0 * 4108 + 4108]  # 获取图像数据部分

                # 将图像数据写入输出文件
                outfile.write(band_data)




    # 写入header
    hdr_file = change_file_extension(output_file, "",".hdr")
    generate_envi_hdr(2048,linescnt,Nbans,"bil",hdr_file)






# 调用函数，提取图像数据并保存为二进制文件
extract_image_data('E:/解压缩linshi/925026/ZY1F_AHSI_VNIR_20250212_210_214_L00000925029.DAT', 'E:/解压缩linshi/925026/output_image_data.bin',76)
