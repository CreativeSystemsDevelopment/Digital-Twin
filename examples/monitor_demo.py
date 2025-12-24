#!/usr/bin/env python3
"""
Example: Using the Agent Monitoring System

This script demonstrates how to use the monitoring system to track
extraction agents working on schematic digitization.
"""

import time
from pathlib import Path
from src.digital_twin.agent_monitor import get_monitor, AgentStatus, TaskPriority


def simulate_extraction_workflow():
    """Simulate a multi-agent extraction workflow."""
    
    print("=" * 70)
    print("Agent Monitoring System - Example Workflow")
    print("=" * 70)
    
    # Initialize monitor
    monitor = get_monitor(Path("data/monitor_state.json"))
    
    print("\n📋 Step 1: Registering extraction agents...")
    
    # Register multiple agents for parallel extraction
    agent1_id = monitor.register_agent(
        name="Extractor-Primary",
        agent_type="gemini_extractor",
        metadata={"model": "gemini-2.5-pro", "priority": "high"}
    )
    print(f"   ✓ Primary extractor registered: {agent1_id[:8]}...")
    
    agent2_id = monitor.register_agent(
        name="Extractor-Secondary",
        agent_type="gemini_extractor",
        metadata={"model": "gemini-2.5-flash", "priority": "normal"}
    )
    print(f"   ✓ Secondary extractor registered: {agent2_id[:8]}...")
    
    validator_id = monitor.register_agent(
        name="Validator",
        agent_type="validator",
        metadata={"checks": ["completeness", "accuracy"]}
    )
    print(f"   ✓ Validator registered: {validator_id[:8]}...")
    
    print("\n📝 Step 2: Assigning extraction tasks...")
    
    # Assign tasks to agents
    task1_id = monitor.assign_task(
        agent_id=agent1_id,
        description="Extract pages 6-50 (primary schematics)",
        task_type="page_extraction",
        priority=TaskPriority.HIGH,
        pages=list(range(6, 51)),
        metadata={"section": "main_circuits"}
    )
    print(f"   ✓ Task 1 assigned to Primary: Pages 6-50")
    
    task2_id = monitor.assign_task(
        agent_id=agent2_id,
        description="Extract pages 51-100 (secondary circuits)",
        task_type="page_extraction",
        priority=TaskPriority.NORMAL,
        pages=list(range(51, 101)),
        metadata={"section": "auxiliary_circuits"}
    )
    print(f"   ✓ Task 2 assigned to Secondary: Pages 51-100")
    
    task3_id = monitor.assign_task(
        agent_id=validator_id,
        description="Validate extracted data",
        task_type="validation",
        priority=TaskPriority.NORMAL,
        metadata={"validation_rules": ["schema", "references"]}
    )
    print(f"   ✓ Task 3 assigned to Validator: Data validation")
    
    print("\n🚀 Step 3: Starting extraction workflow...")
    
    # Start agent 1
    monitor.update_agent_status(agent1_id, AgentStatus.RUNNING, "Initializing Gemini client")
    monitor.update_task_status(task1_id, AgentStatus.RUNNING)
    print(f"   ⚙️  Primary extractor started")
    
    # Simulate progressive extraction
    for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
        time.sleep(0.5)  # Simulate work
        pages_done = int(45 * progress) + 6
        monitor.update_task_progress(
            task1_id, 
            progress,
            pages_completed=list(range(6, pages_done))
        )
        monitor.heartbeat(agent1_id, task1_id)
        print(f"   📊 Primary progress: {progress:.0%} ({pages_done - 6}/45 pages)")
    
    # Complete task 1
    monitor.update_task_status(task1_id, AgentStatus.COMPLETED)
    monitor.update_agent_status(agent1_id, AgentStatus.COMPLETED, "Extraction finished")
    print(f"   ✅ Primary extractor completed!")
    
    # Start agent 2
    print(f"\n   ⚙️  Secondary extractor started")
    monitor.update_agent_status(agent2_id, AgentStatus.RUNNING, "Processing secondary pages")
    monitor.update_task_status(task2_id, AgentStatus.RUNNING)
    
    # Simulate extraction with fewer updates
    for progress in [0.3, 0.7, 1.0]:
        time.sleep(0.5)
        pages_done = int(50 * progress) + 51
        monitor.update_task_progress(
            task2_id,
            progress,
            pages_completed=list(range(51, pages_done))
        )
        monitor.heartbeat(agent2_id, task2_id)
        print(f"   📊 Secondary progress: {progress:.0%} ({pages_done - 51}/50 pages)")
    
    monitor.update_task_status(task2_id, AgentStatus.COMPLETED)
    monitor.update_agent_status(agent2_id, AgentStatus.COMPLETED, "Extraction finished")
    print(f"   ✅ Secondary extractor completed!")
    
    # Start validator
    print(f"\n   ⚙️  Validator started")
    monitor.update_agent_status(validator_id, AgentStatus.RUNNING, "Validating extracted data")
    monitor.update_task_status(task3_id, AgentStatus.RUNNING)
    
    time.sleep(1)
    monitor.update_task_progress(task3_id, 1.0)
    monitor.update_task_status(task3_id, AgentStatus.COMPLETED)
    monitor.update_agent_status(validator_id, AgentStatus.COMPLETED, "Validation passed")
    print(f"   ✅ Validator completed!")
    
    print("\n📈 Step 4: Final Summary")
    summary = monitor.get_overall_summary()
    print(f"   Total agents: {summary['total_agents']}")
    print(f"   Total tasks: {summary['total_tasks']}")
    print(f"   Completed tasks: {summary['tasks_by_status']['completed']}")
    print(f"   Overall progress: {summary['overall_progress']:.1%}")
    
    print("\n🎯 Step 5: Checking for incomplete work...")
    incomplete = monitor.get_incomplete_tasks()
    if incomplete:
        print(f"   ⚠️  {len(incomplete)} tasks still in progress")
        for task in incomplete:
            print(f"      - {task.description}: {task.status}")
    else:
        print(f"   ✅ All tasks completed!")
    
    print("\n" + "=" * 70)
    print("Workflow Complete! View dashboard at: http://localhost:8000/monitor/dashboard")
    print("=" * 70)


if __name__ == "__main__":
    simulate_extraction_workflow()
