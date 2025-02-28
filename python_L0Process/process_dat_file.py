import struct

from sympy import false


## 解压后的zy1F文件，提取0915后的20个字节，同时计算两帧之间的差距字节
# 原理：
# 理想的文件结构是  3084字节辅助 + 2048*2*76字节图像
# dat文件读取进来后，找到09 15 c0 00开头的字节串，
# 然后截取20个字节保存，同时，再计算和上一个09 15 c0 00相距多少字节，继续写入文件。
# 之后继续寻找下一个09 15 c0 00头。一直到文件结束。
#
# 输入输出：
# 输入解压后的dat文件
# 输出 [距离上一个0915多少字节(4字节) +  0915开始的20个字节]
def process_aux20_file_streaming(input_file, output_file):
    """
    流式读取 input_file，查找每个以 09 15 c0 00 开头的字节串，
    对于每个匹配：如果后续数据至少20字节，则截取20字节写入输出文件，
    并且对于除第一个匹配外，计算当前匹配与上一次匹配之间的字节间隔（4字节，little-endian）写入输出文件。
    """
    pattern = b'\x09\x15\xc0\x00'
    pattern_len = len(pattern)
    extract_len = 20
    chunk_size = 40960  # 每次读取的块大小

    prev_match_abs = None  # 上一个匹配的绝对文件位置
    file_pos = 0           # 当前缓冲区对应的文件起始偏移量
    buffer = b''

    isProcessAll = True       # 是否处理全部数据？
    maxread_size = 2603349342  # 只处理多少字节数据，因为文件可能太大，所以可能我们只处理一部分。
    curread_size = 0;
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                # 文件读完后退出循环
                break
            buffer += chunk

            # 是否处理全部数据？
            if False == isProcessAll :
                curread_size = curread_size+chunk_size
                if curread_size>maxread_size:
                    break

            search_pos = 0
            while True:
                idx = buffer.find(pattern, search_pos)
                if idx == -1:
                    break  # 本次缓冲区内无更多匹配
                # 计算当前匹配的绝对位置
                abs_idx = file_pos + idx
                # 如果从匹配处到缓冲区末尾不足20字节，则跳出循环，等待更多数据
                if len(buffer) - idx < extract_len:
                    break

                segment = buffer[idx:idx+extract_len]
                # 如果不是第一个匹配，则计算间隔，并写入4字节数据（little-endian）
                if prev_match_abs is not None:
                    gap = abs_idx - prev_match_abs
                    fout.write(struct.pack('<I', gap))
                # 写入截取的20字节
                fout.write(segment)
                prev_match_abs = abs_idx
                # 继续向后查找
                search_pos = idx + 1

            # 为防止模式字串或20字节数据跨块，保留缓冲区末尾足够的数据
            # 至少保留 (extract_len - 1) 个字节，确保跨块匹配不会遗漏
            keep = extract_len - 1
            if len(buffer) > keep:
                # 更新已处理的字节数 file_pos
                file_pos += len(buffer) - keep
                buffer = buffer[-keep:]
            # 否则，不做任何处理，等待下次读入

        # 文件结束后，剩余的buffer中如果有匹配但数据不足20字节，则忽略


## 用于读取process_dat_file_streaming的输出文件，判断帧号是否连续。
## 同时还可以判断，帧长是否正确
def check_frame_continuity(file_path, skip_size):
    """
    读取二进制文件，每小段24字节，以 09 15 c0 00 开头，
    提取每小段的第9-12字节（大端组合为32位无符号整数，作为帧号），
    判断帧号是否连续，若不连续则打印出断开的帧号。
    """
    segment_size = 24  # 一行大小
    marker = b'\x09\x15\xc0\x00'
    prev_frame = None

    with open(file_path, 'rb') as f:

        # 跳过需要跳过的字节
        if skip_size > 0:
            f.read(skip_size)

        # 开始处理
        segment_index = 0
        while True:

            segment = f.read(segment_size)
            if len(segment) < segment_size:
                break  # 文件结束

            segment_index += 1

            # 检查小段开头是否为 marker
            if segment[:4] != marker:
                print(f"Segment {segment_index}: marker 不匹配，跳过此段。")
                continue

            # 帧号，提取第9-12字节 (索引8~11)
            frame_bytes = segment[8:12]
            # 大端模式转换为整数
            frame_number = struct.unpack('>I', frame_bytes)[0]

            # 判断是否连续
            if prev_frame is not None:
                if frame_number != prev_frame + 1:
                    print(f"帧号不连续：上一帧 {prev_frame}，当前帧 {frame_number}|{frame_bytes[0]:02x}{frame_bytes[1]:02x}{frame_bytes[2]:02x}{frame_bytes[3]:02x}")
            prev_frame = frame_number

            # 间隔，提取第21-24字节(索引20~23)
            intv_bytes = segment[20:24]
            # 大端模式转换为整数
            intv_number = struct.unpack('<I', intv_bytes)[0]
            if intv_number != 314380:
                print(f"字节间隔不对：上一帧 {prev_frame}，当前帧 {frame_number}|{frame_bytes[0]:02x}{frame_bytes[1]:02x}{frame_bytes[2]:02x}{frame_bytes[3]:02x}")




# 示例调用
if __name__ == '__main__':
    # process_aux20_file_streaming("E:/解压缩linshi/tmp_20250227_115137413_0.dat", "E:/解压缩linshi/frame_NO.dat")  #提取解压后图像的帧号
    check_frame_continuity("E:/解压缩linshi/frame_NO.dat", 24*4)  # 跳过4行空数据，判断帧号是否连续
