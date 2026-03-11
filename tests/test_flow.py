"""
Unit tests for flow control.
"""
import unittest
from unittest.mock import Mock, patch

from sentinel.flow.rule import FlowRule, FlowRuleManager, ControlBehavior
from sentinel.flow.slot import FlowSlot
from sentinel.core.resource import Resource, ResourceWrapper
from sentinel.core.context import Context


class TestFlowRule(unittest.TestCase):
    """Test cases for FlowRule."""
    
    def test_qps_limit(self):
        """Test QPS limiting."""
        rule = FlowRule(resource="test", qps=10)
        
        # First 10 should pass
        for _ in range(10):
            self.assertTrue(rule.can_pass())
        
        # Next should fail (bucket empty)
        self.assertFalse(rule.can_pass())
    
    def test_concurrency_limit(self):
        """Test concurrency limiting."""
        rule = FlowRule(resource="test", thread_count=5)
        
        # Should pass when threads <= 5
        self.assertTrue(rule.can_pass())
    
    def test_flow_rule_manager(self):
        """Test FlowRuleManager."""
        rule1 = FlowRule(resource="api1", qps=100)
        rule2 = FlowRule(resource="api2", qps=200)
        
        FlowRuleManager.load_rules([rule1, rule2])
        
        rules = FlowRuleManager.get_rules_for_resource("api1")
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].qps, 100)
        
        FlowRuleManager.clear_rules()


class TestFlowSlot(unittest.TestCase):
    """Test cases for FlowSlot."""
    
    def test_flow_slot_pass(self):
        """Test flow slot allows passing."""
        slot = FlowSlot()
        resource = Resource("test")
        wrapper = ResourceWrapper(resource)
        context = Context()
        
        # No rules, should pass
        result = slot.entry(wrapper, context)
        self.assertIsNone(result)
    
    def test_flow_slot_block(self):
        """Test flow slot blocks when limit exceeded."""
        # Load a rule that will block
        rule = FlowRule(resource="test", qps=0)  # 0 QPS means always block
        FlowRuleManager.load_rules([rule])
        
        slot = FlowSlot()
        resource = Resource("test")
        wrapper = ResourceWrapper(resource)
        context = Context()
        
        result = slot.entry(wrapper, context)
        self.assertIsNotNone(result)
        
        FlowRuleManager.clear_rules()


if __name__ == "__main__":
    unittest.main()
