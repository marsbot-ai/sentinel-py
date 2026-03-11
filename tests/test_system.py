"""
Unit tests for system protection.
"""
import unittest
from unittest.mock import Mock, patch

from sentinel.system.rule import SystemRule, SystemRuleManager
from sentinel.system.metrics import SystemMetrics


class TestSystemRule(unittest.TestCase):
    """Test cases for SystemRule."""
    
    def test_cpu_protection(self):
        """Test CPU protection."""
        rule = SystemRule(highest_cpu_usage=0.5)
        
        # Mock system metrics
        with patch.object(SystemMetrics, 'get_instance') as mock_get:
            mock_metrics = Mock()
            mock_metrics.get_cpu_usage.return_value = 0.3  # 30% CPU
            mock_get.return_value = mock_metrics
            
            self.assertTrue(rule.check_system_status())
            
            mock_metrics.get_cpu_usage.return_value = 0.9  # 90% CPU
            self.assertFalse(rule.check_system_status())
    
    def test_load_protection(self):
        """Test load average protection."""
        rule = SystemRule(highest_system_load=2.0)
        
        with patch.object(SystemMetrics, 'get_instance') as mock_get:
            mock_metrics = Mock()
            mock_metrics.get_system_load.return_value = 1.0
            mock_get.return_value = mock_metrics
            
            self.assertTrue(rule.check_system_status())
            
            mock_metrics.get_system_load.return_value = 5.0
            self.assertFalse(rule.check_system_status())
    
    def test_system_rule_manager(self):
        """Test SystemRuleManager."""
        rule = SystemRule(highest_cpu_usage=0.8)
        
        SystemRuleManager.load_rules([rule])
        rules = SystemRuleManager.get_rules()
        self.assertEqual(len(rules), 1)
        
        SystemRuleManager.clear_rules()
        rules = SystemRuleManager.get_rules()
        self.assertEqual(len(rules), 0)


class TestSystemMetrics(unittest.TestCase):
    """Test cases for SystemMetrics."""
    
    def test_singleton(self):
        """Test SystemMetrics is singleton."""
        m1 = SystemMetrics.get_instance()
        m2 = SystemMetrics.get_instance()
        self.assertIs(m1, m2)
    
    def test_metrics_collection(self):
        """Test metrics collection."""
        metrics = SystemMetrics.get_instance()
        
        # Just verify methods don't throw
        cpu = metrics.get_cpu_usage()
        self.assertIsInstance(cpu, float)
        
        memory = metrics.get_memory_usage()
        self.assertIsInstance(memory, float)
        
        load = metrics.get_system_load()
        self.assertIsInstance(load, float)
        
        threads = metrics.get_thread_count()
        self.assertIsInstance(threads, int)


if __name__ == "__main__":
    unittest.main()
