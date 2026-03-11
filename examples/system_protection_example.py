"""
Example: System Protection with Sentinel

Demonstrates system-level protection.
"""
import time
from sentinel import Sentinel
from sentinel.system import SystemRule


def test_cpu_protection():
    """Test CPU usage protection."""
    print("=== CPU Protection Test ===")
    
    # Protect when CPU > 80%
    rule = SystemRule(highest_cpu_usage=0.8)
    Sentinel.load_system_rules([rule])
    
    for i in range(10):
        try:
            with Sentinel.entry("api"):
                print(f"Request {i+1}: Passed")
        except Exception as e:
            print(f"Request {i+1}: Blocked - {e}")
        
        time.sleep(0.5)
    
    Sentinel.clear_rules()


def test_load_protection():
    """Test system load protection."""
    print("\n=== System Load Protection Test ===")
    
    # Protect when system load > 4
    rule = SystemRule(highest_system_load=4.0)
    Sentinel.load_system_rules([rule])
    
    for i in range(10):
        try:
            with Sentinel.entry("api"):
                print(f"Request {i+1}: Passed")
        except Exception as e:
            print(f"Request {i+1}: Blocked - {e}")
        
        time.sleep(0.5)
    
    Sentinel.clear_rules()


if __name__ == "__main__":
    test_cpu_protection()
    test_load_protection()
    print("\nAll tests completed!")
