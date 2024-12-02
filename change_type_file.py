import pandas as pd
import json

# เปิดไฟล์ JSON
with open('data.json', 'r') as file:
    data = json.load(file)

# ถ้าไฟล์ JSON เป็น array ของ objects (เช่น รายการผู้ใช้ในตัวอย่าง)
df = pd.json_normalize(data)

# บันทึกเป็นไฟล์ Excel (.xlsx)
df.to_excel('please.xlsx', index=False)

print("ไฟล์ได้ถูกแปลงแล้วเป็น output.xlsx")
