import pytest
import uuid
from app.scheduler.job_queue import JobQueue

@pytest.mark.anyio
async def test_priority_queue_ordering():
    queue = JobQueue()
    
    brand_high = uuid.uuid4()
    brand_normal = uuid.uuid4()
    brand_low = uuid.uuid4()
    
    # Enqueue in jumbled order
    await queue.enqueue(brand_low, priority="LOW")
    await queue.enqueue(brand_high, priority="HIGH")
    await queue.enqueue(brand_normal, priority="NORMAL")
    
    # Assert size
    assert await queue.size() == 3
    
    # Pop items (no active brands running)
    job_1 = await queue.dequeue([])
    job_2 = await queue.dequeue([])
    job_3 = await queue.dequeue([])
    
    # High priority should pop first, then Normal, then Low
    assert job_1["brand_id"] == brand_high
    assert job_1["priority"] == "HIGH"
    
    assert job_2["brand_id"] == brand_normal
    assert job_2["priority"] == "NORMAL"
    
    assert job_3["brand_id"] == brand_low
    assert job_3["priority"] == "LOW"
    
    assert await queue.size() == 0

@pytest.mark.anyio
async def test_queue_concurrency_exclusion():
    queue = JobQueue()
    brand_a = uuid.uuid4()
    brand_b = uuid.uuid4()
    
    await queue.enqueue(brand_a, priority="HIGH")
    await queue.enqueue(brand_b, priority="NORMAL")
    
    # If brand_a is active, it should be skipped, popping brand_b instead
    job = await queue.dequeue([brand_a])
    assert job["brand_id"] == brand_b
    assert job["priority"] == "NORMAL"
