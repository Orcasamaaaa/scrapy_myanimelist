import json

# เปิดไฟล์ JSON และอ่านข้อมูล
with open('users.json', 'r') as file:
    content = file.read()

# ตรวจสอบว่าไฟล์เริ่มต้นด้วย '[' และสิ้นสุดด้วย ']'
if content.startswith('[') and content.endswith(']'):
    # แปลง JSON เป็น list
    try:
        data = json.loads(content)
        print("Successfully loaded JSON data!")
        print(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
else:
    # กรณีที่ไฟล์มีหลาย JSON ที่แยกกัน
    # แยกแต่ละ object ที่ไม่ถูกปิด
    json_objects = content.split('}{')  # แยก object ที่ไม่ปิด
    json_objects = [f'{{{obj}}}' for obj in json_objects]  # เติม {} กลับให้ถูกต้อง

    data = []
    for obj in json_objects:
        try:
            data.append(json.loads(obj))  # แปลง JSON เป็น dictionary
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    # พิมพ์ข้อมูลหรือบันทึกไฟล์ใหม่
    print(data)
