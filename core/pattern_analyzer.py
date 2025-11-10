"""
Pattern Analysis Module
Detects timing patterns, setup correlations, and loss causes
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from core.edgelab_schema import EdgeLabTrade


@dataclass
class SessionPerformance:
    """Performance metrics for a trading session"""
    session_name: str
    total_trades: int
    wins: int
    losses: int
    winrate: float
    avg_win_r: float
    avg_loss_r: float
    expectancy: float
    total_profit_r: float
    verdict: str  # FOCUS, NEUTRAL, AVOID


@dataclass
class TimingIntelligence:
    """Complete timing analysis results"""
    sessions: Dict[str, SessionPerformance]
    best_session: str
    worst_session: str
    hourly_breakdown: Dict[int, float]  # hour -> winrate
    best_hour: int
    overlap_performance: Dict[str, float]  # overlap period -> winrate


class TimingAnalyzer:
    """
    Analyzes when strategy performs best
    
    Detects:
    - Session performance (Tokyo/London/NY)
    - Best/worst hours
    - Day of week patterns
    - Session overlap edges
    """
    
    def __init__(self, trades: List[EdgeLabTrade]):
        self.trades = trades
        
    def analyze(self) -> TimingIntelligence:
        """
        Run complete timing analysis
        
        Returns:
            TimingIntelligence with all timing insights
        """
        
        # Analyze each session
        sessions = self._analyze_sessions()
        
        # Find hourly patterns
        hourly = self._analyze_hours()
        
        # Identify best/worst
        best_session = self._find_best_session(sessions)
        worst_session = self._find_worst_session(sessions)
        best_hour = max(hourly.items(), key=lambda x: x[1])[0] if hourly else 0
        
        # Check overlaps
        overlaps = self._analyze_overlaps()
        
        return TimingIntelligence(
            sessions=sessions,
            best_session=best_session,
            worst_session=worst_session,
            hourly_breakdown=hourly,
            best_hour=best_hour,
            overlap_performance=overlaps
        )
    
    def _analyze_sessions(self) -> Dict[str, SessionPerformance]:
        """Calculate performance per session"""
        
        session_trades = {
            'Tokyo': [],
            'London': [],
            'NY': []
        }
        
        # Group trades by session
        for trade in self.trades:
            hour = trade.timestamp_open.hour
            
            if 0 <= hour < 8:
                session_trades['Tokyo'].append(trade)
            elif 8 <= hour < 14:
                session_trades['London'].append(trade)
            else:
                session_trades['NY'].append(trade)
        
        # Calculate metrics per session
        results = {}
        
        for session_name, trades in session_trades.items():
            if len(trades) == 0:
                continue
                
            perf = self._calculate_session_metrics(session_name, trades)
            results[session_name] = perf
        
        return results
    
    def _calculate_session_metrics(
        self, 
        name: str, 
        trades: List[EdgeLabTrade]
    ) -> SessionPerformance:
        """Calculate metrics for session trades"""
        
        total = len(trades)
        wins = [t for t in trades if t.result == 'WIN']
        losses = [t for t in trades if t.result == 'LOSS']
        
        winrate = len(wins) / total if total > 0 else 0
        
        avg_win_r = np.mean([t.profit_r for t in wins]) if wins else 0
        avg_loss_r = np.mean([t.profit_r for t in losses]) if losses else 0
        
        total_profit_r = sum(t.profit_r for t in trades)
        expectancy = total_profit_r / total if total > 0 else 0
        
        # Determine verdict
        if expectancy > 0.5 and winrate > 0.55:
            verdict = 'FOCUS'
        elif expectancy > 0 and winrate > 0.45:
            verdict = 'NEUTRAL'
        else:
            verdict = 'AVOID'
        
        return SessionPerformance(
            session_name=name,
            total_trades=total,
            wins=len(wins),
            losses=len(losses),
            winrate=winrate,
            avg_win_r=avg_win_r,
            avg_loss_r=avg_loss_r,
            expectancy=expectancy,
            total_profit_r=total_profit_r,
            verdict=verdict
        )
    
    def _analyze_hours(self) -> Dict[int, float]:
        """Calculate winrate per hour"""
        
        hourly_trades = {h: [] for h in range(24)}
        
        for trade in self.trades:
            hour = trade.timestamp_open.hour
            hourly_trades[hour].append(trade)
        
        hourly_wr = {}
        for hour, trades in hourly_trades.items():
            if len(trades) > 0:
                wins = len([t for t in trades if t.result == 'WIN'])
                hourly_wr[hour] = wins / len(trades)
        
        return hourly_wr
    
    def _find_best_session(self, sessions: Dict[str, SessionPerformance]) -> str:
        """Identify best performing session"""
        
        if not sessions:
            return 'Unknown'
        
        best = max(sessions.items(), key=lambda x: x[1].expectancy)
        return best[0]
    
    def _find_worst_session(self, sessions: Dict[str, SessionPerformance]) -> str:
        """Identify worst performing session"""
        
        if not sessions:
            return 'Unknown'
        
        worst = min(sessions.items(), key=lambda x: x[1].expectancy)
        return worst[0]
    
    def _analyze_overlaps(self) -> Dict[str, float]:
        """Check performance during session overlaps"""
        
        # London-NY overlap (14:00-16:00 UTC)
        overlap_trades = [
            t for t in self.trades 
            if 14 <= t.timestamp_open.hour < 16
        ]
        
        if len(overlap_trades) > 0:
            wins = len([t for t in overlap_trades if t.result == 'WIN'])
            overlap_wr = wins / len(overlap_trades)
        else:
            overlap_wr = 0
        
        return {
            'London-NY': overlap_wr
        }
