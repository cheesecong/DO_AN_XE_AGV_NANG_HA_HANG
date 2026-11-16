import time
from pymodbus.client import ModbusSerialClient

# 1. CẤU HÌNH GIAO TIẾP
COM_PORT = 'COM7'     
BAUDRATE = 115200
RFID_ID  = 15

# 2. KHAI BÁO BẢNG LỆNH
TAG_QUEO_TRAI = "20092004"
TAG_QUEO_PHAI = "13032004"
TAG_DI_THANG  = "22072004"

def main():
    client = ModbusSerialClient(port=COM_PORT, baudrate=BAUDRATE, timeout=0.1)

    if not client.connect():
        print(f"❌ Lỗi: Không thể mở cổng {COM_PORT}")
        return

    print("✅ Đã kết nối RS485 thành công.")
    print("📡 Đang chờ thẻ RFID...")
    print("=" * 40)

    last_tag_read = ""

    try:
        while True:
            # Ra lệnh đọc 8 thanh ghi (để lấy đủ 8 số), bắt đầu từ 1003
            resp = client.read_input_registers(address=1003, count=8, device_id=RFID_ID)

            if not resp.isError():
                regs = resp.registers
                
                # Nếu tổng các số trong mảng > 0 (tức là đang có thẻ)
                if sum(regs) > 0:
                    # Ghép thẳng 8 thanh ghi thành chuỗi (VD: [2,2,0,7,2,0,0,4] -> "22072004")
                    ma_the_hien_tai = "".join(str(x) for x in regs)
                    
                    if ma_the_hien_tai != last_tag_read:
                        print(f"[{time.strftime('%H:%M:%S')}] Quét được mã thẻ: {ma_the_hien_tai}")
                        
                        if ma_the_hien_tai == TAG_QUEO_TRAI:
                            print(" ➡️ LỆNH ĐIỀU HƯỚNG: QUẸO TRÁI")
                        
                        elif ma_the_hien_tai == TAG_QUEO_PHAI:
                            print(" ➡️ LỆNH ĐIỀU HƯỚNG: QUẸO PHẢI")
                        
                        elif ma_the_hien_tai == TAG_DI_THANG:
                            print(" ➡️ LỆNH ĐIỀU HƯỚNG: ĐI THẲNG")
                        
                        else:
                            print("  Cảnh báo: Mã thẻ lạ, không có trong hệ thống!")
                        
                        print("-" * 40)
                        last_tag_read = ma_the_hien_tai
                else:
                    # Xóa bộ nhớ đệm khi rút thẻ ra
                    last_tag_read = ""

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng chương trình.")
    finally:
        client.close()

if __name__ == "__main__":
    main()