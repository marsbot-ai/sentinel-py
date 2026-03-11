# Sentinel-Py

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

**⚠️ This is a CLIENT library, NOT a server implementation.**

Python version of [Alibaba Sentinel](https://github.com/alibaba/Sentinel) - A powerful flow control, circuit breaking and system protection library for microservices.

> **Note:** This library allows your Python applications to protect resources with flow control, circuit breaking, and system protection. This is inspired by the official Java implementation.

## Features

- **Flow Control**: QPS and concurrency limiting with warm-up support
- **Circuit Breaking**: Automatic circuit breaker based on error ratio, error count, or slow request ratio
- **System Protection**: Protect your system from overload (CPU, load average, RT, threads, QPS)
- **Real-time Statistics**: Monitor resource metrics in real-time
- **Flexible Rules**: Easy-to-configure rules with various strategies

## Getting Started

### Do I Need a Server?

**No.** Sentinel-Py is a **standalone client library** that works entirely within your Python application. All protection rules are evaluated locally - no external server required.

```python
# This works out of the box - no server needed!
from sentinel import Sentinel
from sentinel.flow import FlowRule

rule = FlowRule(resource="api", qps=100)
Sentinel.load_flow_rules([rule])
```

### Optional: Sentinel Dashboard

For visual monitoring and dynamic rule management, you can optionally deploy the **Sentinel Dashboard** (Java-based):

**Start Dashboard with Docker:**
```bash
docker run --name sentinel-dashboard \
  -p 8858:8858 \
  bladex/sentinel-dashboard:latest
```

**Or download and run:**
```bash
wget https://github.com/alibaba/Sentinel/releases/download/1.8.6/sentinel-dashboard-1.8.6.jar
java -jar sentinel-dashboard-1.8.6.jar --server.port=8858
```

**Access Dashboard:** http://localhost:8858 (login: `sentinel` / `sentinel`)

> **Note:** The dashboard is completely optional. All core protection features work without it.

## Installation

```bash
pip install sentinel-py
```

Or install from source:

```bash
git clone https://github.com/marsbot-ai/sentinel-py.git
cd sentinel-py
pip install -e .
```

## Quick Start

### Basic Flow Control

```python
from sentinel import Sentinel
from sentinel.flow import FlowRule

# Define a flow control rule (100 QPS limit)
rule = FlowRule(resource="hello_api", qps=100)
Sentinel.load_flow_rules([rule])

# Protect your code
@Sentinel.entry("hello_api")
def hello():
    return "Hello World"

# Or using context manager
with Sentinel.entry("hello_api"):
    print("Hello World")
```

### Circuit Breaker

```python
from sentinel import Sentinel
from sentinel.circuit import CircuitBreakerRule, CircuitBreakerStrategy

# Define circuit breaker rule
rule = CircuitBreakerRule(
    resource="unstable_api",
    strategy=CircuitBreakerStrategy.ERROR_RATIO,
    threshold=0.5,  # Open circuit when error ratio > 50%
    time_window_sec=10,
    recovery_timeout_ms=5000
)
Sentinel.load_degrade_rules([rule])

with Sentinel.entry("unstable_api"):
    # If this fails 50% of the time, circuit will open
    call_unstable_service()
```

### System Protection

```python
from sentinel import Sentinel
from sentinel.system import SystemRule

# Define system protection rule
rule = SystemRule(
    highest_cpu_usage=0.8,  # Protect when CPU > 80%
    highest_system_load=4.0  # Protect when load > 4
)
Sentinel.load_system_rules([rule])

with Sentinel.entry("protected_api"):
    # Request will be blocked if system is overloaded
    process_request()
```

## Architecture

```
┌─────────────────┐                           ┌─────────────────┐
│   Your Python   │                           │   Sentinel      │
│   Application   │  ────── Entry ──────►     │   Flow Control  │
│                 │                           │   Circuit Break │
│                 │  ◄──── Exit ─────────     │   System Protect│
└─────────────────┘                           └─────────────────┘
       Client                                          Core
```

## API Reference

### FlowRule

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource` | str | Resource name |
| `qps` | float | QPS limit |
| `thread_count` | int | Concurrent thread limit |
| `control_behavior` | ControlBehavior | DEFAULT, WARM_UP, RATE_LIMITER |

### CircuitBreakerRule

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource` | str | Resource name |
| `strategy` | CircuitBreakerStrategy | ERROR_RATIO, ERROR_COUNT, SLOW_REQUEST_RATIO |
| `threshold` | float | Threshold for triggering |
| `time_window_sec` | int | Statistics time window |
| `recovery_timeout_ms` | int | Time before recovery attempt |

### SystemRule

| Parameter | Type | Description |
|-----------|------|-------------|
| `highest_cpu_usage` | float | Max CPU usage (0.0-1.0) |
| `highest_system_load` | float | Max system load average |
| `avg_rt` | int | Max average response time (ms) |
| `max_thread` | int | Max thread count |
| `qps` | float | Max QPS |

## Examples

See the [examples/](examples/) directory for more usage examples.

## Testing

```bash
python -m unittest discover tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Acknowledgments

This project is inspired by the official [Alibaba Sentinel](https://github.com/alibaba/Sentinel).

This is a **client-only** library implementing Sentinel concepts in Python.
