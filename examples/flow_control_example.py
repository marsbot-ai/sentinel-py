"""
Example: Flow Control with Sentinel

Demonstrates QPS limiting and concurrency control.
"""
import time
import threading
from sentinel import Sentinel
from sentinel.flow import FlowRule, ControlBehavior


def test_qps_limit():
    """Test QPS limiting."""
    print("=== QPS Limit Test ===")
    
    # Allow 10 QPS
    rule = FlowRule(resource="api", qps=10)
    Sentinel.load_flow_rules([rule])
    
    success = 0
    blocked = 0
    
    start = time.time()
    for i in range(20):
        try:
            with Sentinel.entry("api"):
                success += 1
        except Exception as e:
            blocked += 1
            print(f"  Blocked: {e}")
    
    elapsed = time.time() - start
    print(f"Success: {success}, Blocked: {blocked}, Time: {elapsed:.2f}s")
    
    # Clear rules
    Sentinel.clear_rules()


def test_concurrency_limit():
    """Test concurrency limiting."""
    print("\n=== Concurrency Limit Test ===")
    
    # Allow max 3 concurrent threads
    rule = FlowRule(resource="api", thread_count=3)
    Sentinel.load_flow_rules([rule])
    
    results = []
    
    def worker(n):
        try:
            with Sentinel.entry("api"):
                time.sleep(0.5)
                results.append(f"Thread {n}: success")
        except Exception as e:
            results.append(f"Thread {n}: blocked - {e}")
    
    # Start 5 threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    for r in results:
        print(f"  {r}")
    
    Sentinel.clear_rules()


def test_warm_up():
    """Test warm up strategy."""
    print("\n=== Warm Up Test ===")
    
    # Start at 10 QPS, warm up to 100 QPS over 5 seconds
    rule = FlowRule(
        resource="api",
        qps=100,
        control_behavior=ControlBehavior.WARM_UP,
        warm_up_period_sec=5,
        cold_factor=10
    )
    Sentinel.load_flow_rules([rule])
    
    for i in range(5):
        success = 0
        blocked = 0
        
        for _ in range(20):
            try:
                with Sentinel.entry("api"):
                    success += 1
            except:
                blocked += 1
        
        print(f"  Second {i+1}: Success={success}, Blocked={blocked}")
        time.sleep(1)
    
    Sentinel.clear_rules()


if __name__ == "__main__":
    test_qps_limit()
    test_concurrency_limit()
    test_warm_up()
    print("\nAll tests completed!")
