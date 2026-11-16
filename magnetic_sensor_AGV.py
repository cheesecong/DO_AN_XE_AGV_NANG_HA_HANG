import time
from pymodbus.client import ModbusSerialClient


COM_PORT = 'COM7'    
BAUDRATE = 115200
SENSOR_ID = 20        

def unsigned_to_signed(val):
    """
    Hàm ép kiểu từ 16-bit không dấu sang có dấu (Two's complement).
    Giúp đọc được sai số âm (lệch trái) của cảm biến từ.
    """
    if val > 32767:
        return val - 65536
    return val

def main():
    # Khởi tạo kết nối Modbus
    client = ModbusSerialClient(
        port=COM_PORT,
        baudrate=BAUDRATE,
        timeout=0.1
    )

    if not client.connect():
        print(f" Lỗi: Không thể mở cổng {COM_PORT}")
        return

    print(" Đã kết nối RS485 thành công.")
    print(f" Đang đọc Cảm biến từ Hinson (ID {SENSOR_ID})...")
    print("=" * 60)

    try:
        while True:
            # Đọc thanh ghi 1002 (chứa giá trị sai số lệch tâm / tọa độ tính bằng mm)
            # Vì chỉ là 1 con số, ta set count=1
            resp = client.read_input_registers(address=1002, count=1, device_id=SENSOR_ID)
            
            # (Ghi chú: Nếu báo lỗi Exception 2, hãy thử đổi hàm trên thành read_holding_registers)

            if resp.isError():
                print(f" LỖI ĐỌC MODBUS: {resp}")
            else:
                # Lấy giá trị thô từ mảng (phần tử đầu tiên)
                raw_value = resp.registers[0]
                
                # Ép kiểu để lấy sai số âm/dương thực tế
                deviation = unsigned_to_signed(raw_value)
                
                # Xác định hướng lệch để in ra màn hình cho dễ nhìn
                if deviation < 0:
                    huong = " Lệch TRÁI"
                elif deviation > 0:
                    huong = "Lệch PHẢI "
                else:
                    huong = "CÂN BẰNG TÂM"
                    
                print(f"[{time.strftime('%H:%M:%S')}] Tọa độ thô: {raw_value:<5} | Sai số thực tế: {deviation:>4} mm -> {huong}")

            # Tốc độ đọc: 20 lần/giây (50ms)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n Đã dừng chương trình.")
    finally:
        client.close()

if __name__ == "__main__":
    main()