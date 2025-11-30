import psutil
import time
import os

# --- Configuration ---
# Set the CPU usage percentage threshold (e.g., 80.0%)
CPU_THRESHOLD = 80.0

# Set the monitoring interval in seconds
MONITOR_INTERVAL_SECONDS = 2 

def monitor_cpu_health(threshold: float, interval: int):
    print("--- DevOps Server Health Monitor ---")
    print(f"Monitoring CPU usage every {interval} seconds...")
    print(f"Alert Threshold: {threshold}%")
    print("Press Ctrl+C to interrupt and stop the monitoring.")
    print("-" * 40)
    
    while True:
        try:
            cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
            
            # Display current usage for continuous monitoring feedback
            print(f"Current CPU Usage: {cpu_usage:.1f}%")

            # Check if the usage exceeds the predefined threshold
            if cpu_usage > threshold:
                # Display the alert message
                print(f"\n🚨 ALERT! CPU usage exceeds threshold: {cpu_usage:.1f}%\n")
            
            # Pause for the specified interval before the next check
            time.sleep(interval)

        except KeyboardInterrupt:
            # Handle user interruption (Ctrl+C) gracefully
            print("\nMonitoring interrupted by user (Ctrl+C). Exiting...")
            break
        
        except Exception as e:
            # General error handling for any other exceptions (e.g., psutil issues)
            print(f"\n[ERROR] An unexpected error occurred: {e}")
            # Wait longer after an error before retrying to prevent rapid error loops
            time.sleep(5)

if __name__ == "__main__":
    monitor_cpu_health(CPU_THRESHOLD, MONITOR_INTERVAL_SECONDS)