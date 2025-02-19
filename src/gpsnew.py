import serial
from typing import Optional, Tuple

class GPSModule:
    def __init__(self, port: str = "/dev/serial0", baud_rate: int = 9600):
        """
        GPSモジュールを初期化
        :param port: シリアルポート
        :param baud_rate: ボーレート
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = None

    def connect(self):
        """シリアル接続を初期化"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
            print("GPS module connected.")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to GPS module: {e}")

    def disconnect(self):
        """シリアル接続を閉じる"""
        if self.serial_connection:
            self.serial_connection.close()
            print("GPS module disconnected.")

    def parse_nmea_sentence(self, sentence: str) -> Tuple[Optional[float], Optional[float], Optional[int], Optional[str], Optional[float]]:
        """
        NMEA文を解析し、座標、衛星数、時刻を取得
        :param sentence: NMEA文
        :return: (緯度, 経度, 衛星数, 時刻)
        """
        try:
            parts = sentence.split(',')
            if parts[0] == "$GPGGA":
                # 時刻
                utc_time = parts[1][:6]

                # 緯度と経度
                raw_lat = parts[2]
                lat_dir = parts[3]
                raw_lon = parts[4]
                lon_dir = parts[5]

                # 衛星数
                satellite_count = int(parts[7]) if parts[7].isdigit() else None

                #DOP値（座標の精度）
                dop = parts[8]

                # 座標変換
                lat = float(raw_lat[:2]) + float(raw_lat[2:]) / 60.0 if raw_lat else None
                if lat_dir == "S":
                    lat = -lat

                lon = float(raw_lon[:3]) + float(raw_lon[3:]) / 60.0 if raw_lon else None
                if lon_dir == "W":
                    lon = -lon

                return lat, lon, satellite_count, utc_time, dop

        except (ValueError, IndexError):
            pass  # 無効なデータはスキップ
        return None, None, None, None, None

    def get_gps_data(self) -> Tuple[Optional[float], Optional[float], Optional[int], Optional[str], Optional[float]]:
        """
        GPSデータをリアルタイムで取得
        :return: (緯度, 経度, 衛星数, 時刻)
        """
        if not self.serial_connection:
            raise ConnectionError("GPS module is not connected.")
        
        try:
            while True:
                line = self.serial_connection.readline().decode('ascii', errors='replace').strip()
                if line.startswith("$GPGGA"):
                    return self.parse_nmea_sentence(line)
        except KeyboardInterrupt:
            print("\nGPS data fetching stopped by user.")
        except Exception as e:
            print(f"Error while reading GPS data: {e}")
        return None, None, None, None, None

# メインプログラム例
if __name__ == "__main__":
    gps = GPSModule()

    try:
        gps.connect()
        print("Fetching GPS data...")
        while True:
            lat, lon, satellites, utc_time, dop = gps.get_gps_data()
            if lat is not None and lon is not None:
                print(f"Latitude: {lat:.6f}, Longitude: {lon:.6f}, Satellites: {satellites}, Time: {utc_time}, DOP: {dop}")
                # ロギングを追加する場合、以下に記述
            # Example: log_to_file(lat, lon, satellites, time_utc, dop)
            else:
                break
    except KeyboardInterrupt:
        print("Terminating program.")
    finally:
        gps.disconnect()

