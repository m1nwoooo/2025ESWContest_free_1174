import subprocess
import sys
import time

def update_in_place_monitor():
    command = [
        "sudo", "stdbuf", "-oL",
        "wfb_rx",
        "-p", "10",
        "-c", "127.0.0.1",
        "-u", "6011",
        "-K", "/etc/drone.key",
        "-i", "7669206",
        "wlxfc221c30076b",
        "-s", "1000"
    ]

    print("--- 실시간 링크 품질 모니터링 ---")
    print(f"실행 명령어: {' '.join(command)}\n")

    process = None
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        print(">> wfb_rx 프로세스 시작. 모니터링을 시작합니다...\n")
        
        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
            
            try:
                if "RX_ANT" in line:
                    parts = line.strip().split()
                    rssi_chunk = parts[-1]
                    rssi_values_str = rssi_chunk.split(':')
                    rssi_values = [int(val) for val in rssi_values_str if val.lstrip('-').isdigit() and int(val) < 0]

                    if rssi_values:
                        best_rssi = max(rssi_values)
                        quality_score = calculate_link_quality(best_rssi)
                        bar = '█' * int(quality_score / 2) + ' ' * (50 - int(quality_score / 2))
                        timestamp = time.strftime('%H:%M:%S')
                        
                        output_line = f"[{timestamp}] Best RSSI: {best_rssi:4d} dBm | 품질: {quality_score:6.2f}/100 | [{bar}]"
                        print(output_line, end='\r', flush=True)

            except (IndexError, ValueError):
                pass
    
    except KeyboardInterrupt:
        print("\n>> 사용자에 의해 모니터링이 중단되었습니다.")

    except Exception as e:
        print(f"\n스크립트 실행 중 예외 발생: {e}")
        
    finally:
        if process:
            process.kill()
            process.wait()
        print("\n>> 모니터링 시스템을 종료합니다.")


def calculate_link_quality(rssi):
    if rssi <= -90: return 0.0
    if rssi >= -50: return 100.0
    return 100 * (rssi - (-90)) / ((-50) - (-90))


if __name__ == "__main__":
    update_in_place_monitor()
