# 用于从一个标准envi的BIL图像，出一个单波段png


import numpy as np
from PIL import Image

def create_image_from_dat(dat_file, tar_band, output_png):
    """
    读取 dat 文件，该文件由连续排列的图像帧组成，每帧大小为 2048*2*76 字节（共 311296 字节）。
    从每一帧中提取前 4096 字节（假设为一行图像数据），依次作为新图像的一行，
    最终生成的新图像宽度为 4096 像素，高度为帧数，并保存为 PNG 文件。
    """
    """
    读取 dat 文件，该文件由连续排列的图像帧组成，每帧大小为 2048*2*76 = 311296 字节。
    每帧的前4096字节（即2048个像素，每像素2字节，little-endian）作为新图像的一行。
    生成的图像宽度为2048像素，高度为帧数；同时将16位数据归一化到0-255范围内（简单做法：右移8位）。
    最后保存为PNG文件。
    """
    frame_size = 2048 * 2 * 76  # 每帧总字节数 311296
    row_bytes = 4096  # 每帧前4096字节，用作一行图像数据

    rows = []

    # framecnt = 0;
    with open(dat_file, 'rb') as f:
        while True:
            frame = f.read(frame_size)
            if not frame or len(frame) < frame_size:
                break
            # 提取前4096字节数据
            row_data = frame[tar_band*row_bytes: tar_band*row_bytes + row_bytes]
            # 将4096字节数据转换为2048个16位整数（little-endian）
            pixels_16 = np.frombuffer(row_data, dtype='<u2')
            # 将16位像素转换为8位（简单归一化方法：右移8位）
            # pixels_8 = (pixels_16 >> 8).astype(np.uint8)
            pixels_8 = (pixels_16.astype(np.float32) / 500 * 255).clip(0, 255).astype(np.uint8)  # 图像增强
            rows.append(pixels_8)

            # framecnt = framecnt+1
            # if framecnt>3000:
            #     break;

    if not rows:
        print("没有读取到任何帧数据！")
        return

    # 组合所有行，生成二维数组（高度为帧数，宽度为2048）
    image_array = np.stack(rows, axis=0)
    # 生成灰度图像
    img = Image.fromarray(image_array, mode='L')
    img.save(output_png)
    print(f"PNG图像已保存为 {output_png}")


def create_rgb_image_from_dat(dat_file, tar_bands, output_png):
    """
    读取 dat 文件，该文件由连续排列的图像帧组成，每帧大小为 2048*2*76 = 311296 字节。
    每一帧实际上是一行图像数据，其中包含 76 个波段，每个波段占 4096 字节（即 2048 个像素，16 位 little-endian）。
    函数从每一帧中提取 tar_bands 指定的三个波段的数据（例如 (0,1,2)），
    分别归一化后组合为一行 RGB 像素数据，最后所有帧堆叠生成一幅 RGB 图像，
    图像宽度为 2048 像素，高度为帧数。
    """
    frame_size = 2048 * 2 * 76  # 每帧字节数 311296
    row_bytes = 4096            # 每个波段的数据大小

    rows = []
    with open(dat_file, 'rb') as f:
        while True:
            frame = f.read(frame_size)
            if not frame or len(frame) < frame_size:
                break

            channels = []
            for b in tar_bands:
                # 从帧中提取指定波段的数据
                row_data = frame[b * row_bytes: b * row_bytes + row_bytes]
                # 将数据转换为 2048 个 16 位整数
                pixels_16 = np.frombuffer(row_data, dtype='<u2')
                # 数据归一化处理：这里用简单的线性变换（根据实际情况可调整）
                pixels_8 = (pixels_16.astype(np.float32) / 4000 * 255).clip(0, 255).astype(np.uint8)
                channels.append(pixels_8)
            # 将三个通道堆叠为一个 (2048, 3) 的数组，即一行 RGB 数据
            row_rgb = np.stack(channels, axis=-1)
            rows.append(row_rgb)

    if not rows:
        print("没有读取到任何帧数据！")
        return

    # 堆叠所有行，生成最终图像（高度为帧数，宽度为2048，通道数为3）
    image_array = np.stack(rows, axis=0)
    img = Image.fromarray(image_array, mode='RGB')
    img.save(output_png)
    print(f"PNG图像已保存为 {output_png}")


# 示例调用
if __name__ == '__main__':
    # create_image_from_dat('E:/解压缩linshi/all_image.dat', 0,'E:/解压缩linshi/all_image.png')
    create_rgb_image_from_dat('E:/解压缩linshi/20250328图像分析数据（原始+0级朱海健）/结果/vnir/ZY02E-VNIR_LOSSLESS(2048x76)_20250403_163249840_1.dat', [30-1,19-1,10-1],'E:/解压缩linshi/20250328图像分析数据（原始+0级朱海健）/结果/vnir/vnir.png')