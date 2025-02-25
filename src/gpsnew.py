import serial
from typing import Optional, Tuple
import math

import logwrite

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
        self.log = logwrite.MyLogging()

    def connect(self):
        """シリアル接続を初期化"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=1)
#            print("GPS module connected.")
            self.log.write("GPS module connected.","INFO")
        except Exception as e:
            self.log.write("Failed to connect to GPS module","INFO")
            raise ConnectionError(f"Failed to connect to GPS module: {e}")

    def disconnect(self):
        """シリアル接続を閉じる"""
        if self.serial_connection:
            self.serial_connection.close()
#            print("GPS module disconnected.")
            self.log.write("GPS module disconnected.","INFO")

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
            self.log.write("GPS module is not connected.","INFO")
            raise ConnectionError("GPS module is not connected.")
        
        try:
            while True:
                line = self.serial_connection.readline().decode('ascii', errors='replace').strip()
                if line.startswith("$GPGGA"):
                    return self.parse_nmea_sentence(line)
                self.serial_connection.reset_input_buffer()
        except KeyboardInterrupt:
            print("\nGPS data fetching stopped by user.")
        except Exception as e:
            print(f"Error while reading GPS data: {e}")
        return None, None, None, None, None

def calculate_target_distance_angle(current_coordinate,previous_coordinate,goal_coordinate):
    coordinate_diff_goal = {
        "lat":(goal_coordinate["lat"]-current_coordinate["lat"]),
        "lon":(goal_coordinate["lon"]-current_coordinate["lon"])
    }
    degree_for_goal = math.atan2(
        coordinate_diff_goal["lon"],coordinate_diff_goal["lat"]
    ) / math.pi * 180

    coordinate_diff_me = { 'lat' : (current_coordinate['lat'] - previous_coordinate['lat']), 
                                    'lon' : (current_coordinate['lon'] - previous_coordinate['lon'])}
    degree_for_me = math.atan2(
        coordinate_diff_me['lon'], coordinate_diff_me['lat']
    ) / math.pi * 180
    

    degree = degree_for_goal - degree_for_me
    degree = (degree + 360) if (degree < -180) else degree
    dgeree = (degree - 360) if (180 < degree) else degree

    distance = math.sqrt(coordinate_diff_goal["lat"] ** 2 + coordinate_diff_goal["lon"] ** 2) * math.pow(10,5)#m単位で距離を表現
    if distance <= 5:
        #5m以内
        result = {"dir":"Immediate","deg":"0","distance":distance}
        return result
    else:
        if degree <= -45:
            print(f"degree:{degree}")
            result = {"dir":"left","deg":degree,"distance":distance}
            return result
        elif degree >= 45:
            print(f"degree:{degree}")
            result = {"dir":"right","deg":degree,"distance":distance}
            return result
        else:
            print(f"degree:{degree}")
            result = {"dir":"forward","deg":degree,"distance":distance}
            return result

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
                print("Waiting")
    except KeyboardInterrupt:
        print("Terminating program.")
    finally:
        gps.disconnect()

