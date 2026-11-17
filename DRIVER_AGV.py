
import serial
import time
import msvcrt
import math


# =====================================================
# TINH CRC16 MODBUS
# =====================================================
def ModbusCRC(data):
    crc = 0xFFFF

    for byte in data:
        crc ^= byte

        for i in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    return crc


# =====================================================
# KHOI TAO MODBUS RTU
# =====================================================
def InitModbus(comPort, baudrate, slaveID):

    print("\n========================================")
    print("KHOI TAO MODBUS RTU")
    print("========================================")

    print("COM Port  :", comPort)
    print("Slave ID  :", slaveID)
    print("Baudrate  :", baudrate)
    print("Data bits : 8")
    print("Parity    : None")
    print("Stop bits : 1")

    try:
        ser = serial.Serial(
            port=comPort,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.2,
            write_timeout=0.2
        )

        print("\nKhoi tao Modbus thanh cong!")

        return ser

    except serial.SerialException as e:
        print("LOI MO CONG COM:", e)
        return None


# =====================================================
# GHI DU LIEU VAO THANH GHI MODBUS - FC16
# =====================================================
def WriteRegister16(ser, slaveID, reg, value):

    # Chuyen gia tri ve so nguyen 16 bit
    value = int(value)

    if not 0 <= value <= 65535:
        raise ValueError("Gia tri thanh ghi phai tu 0 den 65535")

    # Tao frame Modbus RTU
    frame = bytearray(11)

    frame[0] = slaveID
    frame[1] = 0x10

    frame[2] = (reg >> 8) & 0xFF
    frame[3] = reg & 0xFF

    frame[4] = 0x00
    frame[5] = 0x01

    frame[6] = 0x02

    frame[7] = (value >> 8) & 0xFF
    frame[8] = value & 0xFF

    # Tinh CRC
    crc = ModbusCRC(frame[:9])

    frame[9] = crc & 0xFF
    frame[10] = (crc >> 8) & 0xFF

    # Gui du lieu qua RS485
    ser.write(frame)
    ser.flush()


# =====================================================
# CHUONG TRINH CHINH
# =====================================================
def main():

    # =========================================
    # THONG SO MODBUS
    # =========================================

    comPort = "COM7"
    baudrate = 115200
    slaveID = 10

    # =========================================
    # KHOI TAO MODBUS
    # =========================================

    ser = InitModbus(comPort, baudrate, slaveID)

    if ser is None:
        print("Khoi tao Modbus that bai!")
        return

    print("\nModbus da san sang!")

    try:

        # =========================================
        # THONG SO CO KHI
        # =========================================

        wheel_radius_cm = 9
        pi = 3.14

        Khoang_cach_2_banh = 58

        # =========================================
        # NHAP VAN TOC XE
        # =========================================

        van_toc_xe = float(
            input("Nhap van toc xe (cm/s): ")
        )

        Toc_do_dong_co = (
            van_toc_xe * 30 * 60 /
            (2 * pi * wheel_radius_cm)
        )

        # =========================================
        # NHAP VAN TOC GOC
        # =========================================

        W_bo_cua = float(
            input("Nhap toc do goc khi bo cua (rad/s): ")
        )

        # =========================================
        # TINH VAN TOC 2 BANH
        # =========================================

        V_left = (
            van_toc_xe -
            (W_bo_cua * Khoang_cach_2_banh / 2)
        )

        V_right = (
            van_toc_xe +
            (W_bo_cua * Khoang_cach_2_banh / 2)
        )

        Toc_do_dong_co_left = (
            V_left * 30 * 60 /
            (2 * pi * wheel_radius_cm)
        )

        Toc_do_dong_co_right = (
            V_right * 30 * 60 /
            (2 * pi * wheel_radius_cm)
        )

        # Chuyen RPM sang so nguyen
        Toc_do_dong_co = int(Toc_do_dong_co)

        Toc_do_dong_co_left = int(Toc_do_dong_co_left)

        Toc_do_dong_co_right = int(Toc_do_dong_co_right)

        print("\n========================================")
        print("KET QUA TINH TOAN")
        print("========================================")

        print("RPM dong co :", Toc_do_dong_co)
        print("RPM banh trai :", Toc_do_dong_co_left)
        print("RPM banh phai :", Toc_do_dong_co_right)

        print("\n========================================")
        print("DIEU KHIEN XE AGV")
        print("========================================")

        print("W : Tien")
        print("S : Lui")
        print("A : Re trai")
        print("F : Re phai")
        print("ESC : Thoat chuong trinh")

        # =========================================
        # VONG LAP DIEU KHIEN
        # =========================================

        while True:

            key = msvcrt.getch()

            # Chuyen phim thanh chu thuong
            key = key.decode("utf-8").lower()

            # =====================================
            # THOAT CHUONG TRINH
            # =====================================

            if key == '\x1b':
                print("\nThoat chuong trinh!")
                break

            # =====================================
            # PHIM F
            # =====================================

            if key == 'f':

                WriteRegister16(ser, slaveID, 2000, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2000, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2001, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2002, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2003, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2004, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2005, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2006, Toc_do_dong_co_left)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2007, Toc_do_dong_co_right)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2008, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2009, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2010, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2011, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2012, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2013, 0)

            # =====================================
            # PHIM A
            # =====================================

            if key == 'a':

                WriteRegister16(ser, slaveID, 2000, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2000, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2001, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2002, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2003, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2004, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2005, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2006, Toc_do_dong_co_right)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2007, Toc_do_dong_co_left)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2008, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2009, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2010, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2011, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2012, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2013, 0)

            # =====================================
            # PHIM S
            # =====================================

            if key == 's':

                WriteRegister16(ser, slaveID, 2000, 1)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2000, 0)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2001, 1)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2002, 1)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2003, 1)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2004, 0)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2005, 1)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2006, Toc_do_dong_co)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2007, Toc_do_dong_co)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2008, 0)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2009, 1)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2010, 0)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2011, 0)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2012, 0)
                time.sleep(0.02)

                WriteRegister16(ser, slaveID, 2013, 0)

            # =====================================
            # PHIM W
            # =====================================

            if key == 'w':

                WriteRegister16(ser, slaveID, 2000, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2000, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2001, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2002, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2003, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2004, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2005, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2006, Toc_do_dong_co)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2007, Toc_do_dong_co)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2008, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2009, 1)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2010, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2011, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2012, 0)
                time.sleep(0.03)

                WriteRegister16(ser, slaveID, 2013, 0)

    except Exception as e:
        print("\nLOI:", e)

    finally:

        # Dong cong COM khi thoat
        if ser.is_open:
            ser.close()

        print("Da dong cong COM!")


# =====================================================
# CHAY CHUONG TRINH
# =====================================================

if __name__ == "__main__":
    main()
