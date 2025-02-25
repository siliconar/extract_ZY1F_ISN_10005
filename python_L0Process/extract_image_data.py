import struct
import os

def change_file_extension(input_file, new_addname, new_extension):
    # 分离文件名和扩展名
    base_name, _ = os.path.splitext(input_file)
    # 拼接新的文件名和扩展名
    new_file = base_name + new_addname + new_extension
    return new_file



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

def generate_envi_hdr(samples, lines, bands, interleave, output_file):
    # 根据提供的信息生成HDR内容
    header = f"""ENVI
description = {{ GEO-TIFF File Imported into ENVI [Thu Jul 08 09:11:57 2021]}}
samples = {samples}
lines   = {lines}
bands   = {bands}
data type = 12
interleave = {interleave}
file type = ENVI Standard
header offset = 0
byte order = 0
map info = {{UTM, 1.000, 1.000, 787872.000, 5414784.000, 9.600000e+001, 9.600000e+001, 50, North, WGS-84, units=Meters}}
coordinate system string = {{PROJCS["UTM_Zone_50N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",117.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]}}
x start = 0
y start = 0
band names = {{
 Band 1}}
wavelength units = Unknown
sensor type = Unknown
"""

    # 将生成的HDR内容写入文件
    with open(output_file, 'w') as f:
        f.write(header)






# 调用函数，提取图像数据并保存为二进制文件
extract_image_data('E:/BaiduNetdiskDownload/925843/ZY1F_AHSI_VNIR_20250213_760_129_L00000925843.DAT', 'E:/BaiduNetdiskDownload/925843/output_image_data.bin',76)
