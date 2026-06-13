"""
state_manager.py — 采集状态管理模块

跟踪每个数据源的上次采集时间，支持增量采集。
状态存储在 data/collect_state.json
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional

STATE_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'collect_state.json')


def _load_state() -> dict:
    """Load state from JSON file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_state(state: dict):
    """Save state to JSON file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_last_fetch_time(source_name: str) -> Optional[str]:
    """
    Get the last fetch time for a source.

    Returns:
        ISO 8601 datetime string, or None if never fetched
    """
    state = _load_state()
    return state.get(source_name, {}).get('last_fetch_time')


def update_fetch_time(source_name: str, count: int = 0, notes: str = ''):
    """
    Update the last fetch time for a source to now.

    Args:
        source_name: Source identifier (e.g. 'gdpr_tracker', 'ftc')
        count: Number of cases collected in this run
        notes: Optional notes about this run
    """
    state = _load_state()
    now = datetime.now(timezone.utc).isoformat()

    if source_name not in state:
        state[source_name] = {}

    state[source_name]['last_fetch_time'] = now
    state[source_name]['last_count'] = count
    state[source_name]['last_notes'] = notes

    _save_state(state)


def get_state_summary() -> dict:
    """Get full state summary."""
    return _load_state()
