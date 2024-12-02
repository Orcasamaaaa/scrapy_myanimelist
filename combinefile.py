import pandas as pd
import os

def combine_selected_xlsx_files(file_list, output_filename='combined_output.xlsx'):
    # สร้าง list เพื่อเก็บ DataFrame จากไฟล์ที่เลือก
    all_data_frames = []

    for file_path in file_list:
        if os.path.exists(file_path) and file_path.endswith('.xlsx'):  # ตรวจสอบว่าไฟล์มีอยู่และเป็น .xlsx
            print(f"Reading file: {file_path}")
            # อ่านไฟล์ .xlsx
            df = pd.read_excel(file_path)
            # เพิ่มข้อมูลจากไฟล์นี้ไปยัง list
            all_data_frames.append(df)
        else:
            print(f"File not found or invalid format: {file_path}")

    # รวมข้อมูลทั้งหมดใน list
    combined_df = pd.concat(all_data_frames, ignore_index=True)

    # บันทึกข้อมูลรวมลงในไฟล์ใหม่
    combined_df.to_excel(output_filename, index=False)
    print(f"Combined file saved as {output_filename}")

# ตัวอย่างการใช้ฟังก์ชัน
file_list = [
    'anime_data_0_5000.xlsx',
    'anime_data_5000_10000.xlsx',
    'anime_data_10000_15000.xlsx',
    'anime_data_15000_20000.xlsx',
    'anime_data_20000_25000.xlsx',
]

combine_selected_xlsx_files(file_list, 'animedata_combine.xlsx')
