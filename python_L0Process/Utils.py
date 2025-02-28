
import  os

def change_file_extension(input_file, new_addname, new_extension):
    # 分离文件名和扩展名
    base_name, _ = os.path.splitext(input_file)
    # 拼接新的文件名和扩展名
    new_file = base_name + new_addname + new_extension
    return new_file



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
wavelength units = Unknown
sensor type = Unknown
"""

    # 将生成的HDR内容写入文件
    with open(output_file, 'w') as f:
        f.write(header)

