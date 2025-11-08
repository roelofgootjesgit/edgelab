"""
analyzer.py
===========

Performance analysis engine for EdgeLab.
Calculates trading metrics from EdgeLabTrade objects.

Usage:
    analyzer = BasicAnalyzer()
    results = analyzer.calculate(trades)
    
Metrics Calculated:
- Basic: WR, PF, Expectancy, Avg Win/Loss, Max DD
- Advanced: ESI, PVS, Sharpe Ratio
- Patterns: Session performance, time analysis, directional bias

Author: EdgeLab Development Team
Version: 1.0
"""

from typing import List
import statistics
from core.edgelab_schema import EdgeLabTrade, AnalysisResult


class BasicAnalyzer:
    """
    Calculate fundamental trading metrics.
    
    Metrics calculated:
    - Total trades
    - Win rate (%)
    - Profit factor
    - Expectancy (R-multiple)
    - Average win/loss
    - Max drawdown
    
    Plus advanced metrics via AdvancedAnalyzer integration.
    """
    
    def __init__(self):
        pass
    
    def calculate(self, trades: List[EdgeLabTrade]) -> AnalysisResult:
        """
        Calculate all basic metrics from trade list.
        
        Args:
            trades: List of EdgeLabTrade objects
            
        Returns:
            AnalysisResult with calculated metrics
            
        Raises:
            ValueError: If trades list is empty
        """
        
        if not trades:
            raise ValueError("Cannot analyze empty trade list")
        
        # Calculate basic counts
        total_trades = len(trades)
        wins = [t for t in trades if t.result == "WIN"]
        losses = [t for t in trades if t.result == "LOSS"]
        timeouts = [t for t in trades if t.result == "TIMEOUT"]
        
        num_wins = len(wins)
        num_losses = len(losses)
        num_timeouts = len(timeouts)
        
        # Win Rate
        winrate = (num_wins / total_trades) * 100 if total_trades > 0 else 0
        
        # Profit calculations
        total_profit = sum(t.profit_r for t in trades)
        gross_profit = sum(t.profit_r for t in wins)
        gross_loss = abs(sum(t.profit_r for t in losses))
        
        # Profit Factor
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy (average R per trade)
        expectancy = total_profit / total_trades if total_trades > 0 else 0
        
        # Average Win/Loss
        avg_win = gross_profit / num_wins if num_wins > 0 else 0
        avg_loss = gross_loss / num_losses if num_losses > 0 else 0
        
        # Max Drawdown (simple cumulative approach)
        max_dd = self._calculate_max_drawdown(trades)
        
        # Advanced metrics - calculate using AdvancedAnalyzer
        advanced = AdvancedAnalyzer()
        esi_score = advanced.calculate_esi(trades)
        pvs_score = advanced.calculate_pvs(total_trades, winrate, profit_factor, max_dd)
        sharpe = advanced.calculate_sharpe_ratio(trades)
        
        # Pattern analysis - using PatternAnalyzer
        pattern = PatternAnalyzer()
        best_session = pattern.find_best_session(trades)
        best_hour = pattern.find_best_hour(trades)
        long_wr, short_wr = pattern.calculate_directional_winrates(trades)
        
        # Generate recommendation
        insight = InsightGenerator()
        recommendation = insight.generate_recommendation(
            winrate=winrate,
            profit_factor=profit_factor,
            esi=esi_score,
            pvs=pvs_score,
            best_session=best_session
        )
        
        # Build result
        return AnalysisResult(
            total_trades=total_trades,
            wins=num_wins,
            losses=num_losses,
            winrate=round(winrate, 2),
            profit_factor=round(profit_factor, 2),
            expectancy=round(expectancy, 2),
            total_profit_r=round(total_profit, 2),
            avg_win_r=round(avg_win, 2),
            avg_loss_r=round(avg_loss, 2),
            max_drawdown_pct=round(max_dd, 2),
            
            # Advanced metrics
            esi=round(esi_score, 2),
            pvs=round(pvs_score, 2),
            sharpe_ratio=sharpe,
            
            # Pattern analysis
            best_session=best_session,
            best_hour=best_hour,
            long_winrate=round(long_wr, 2),
            short_winrate=round(short_wr, 2),
            
            # Insights
            recommendation=recommendation
        )
    
    def _calculate_max_drawdown(self, trades: List[EdgeLabTrade]) -> float:
        """
        Calculate maximum drawdown percentage.
        
        Approach: Cumulative equity curve method
        """
        
        equity = [100.0]  # Start at 100%
        
        for trade in trades:
            # Simple assumption: each trade risks 1% of equity
            # Profit/loss in R-multiples translates to % change
            change_pct = trade.profit_r * 1.0
            new_equity = equity[-1] * (1 + change_pct / 100)
            equity.append(new_equity)
        
        # Find maximum peak-to-trough drawdown
        peak = equity[0]
        max_dd = 0.0
        
        for value in equity:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd


class AdvancedAnalyzer:
    """
    Calculate advanced metrics for Pro/Elite tiers.
    
    Metrics:
    - ESI (Edge Stability Index): measures consistency
    - PVS (Prop Verification Score): prop firm readiness
    - Sharpe Ratio: risk-adjusted returns
    """
    
    def __init__(self):
        pass
    
    def calculate_esi(self, trades: List[EdgeLabTrade]) -> float:
        """
        Edge Stability Index: measures if edge is consistent over time.
        
        Method:
        1. Split trades into 4 quarters
        2. Calculate winrate per quarter
        3. ESI = 1 - (StdDev / Mean)
        
        Returns:
            Float 0-1 (higher = more stable)
        """
        
        if len(trades) < 4:
            return 0.0  # Not enough data
        
        # Split into 4 equal parts
        chunk_size = len(trades) // 4
        quarters = [
            trades[i*chunk_size:(i+1)*chunk_size] 
            for i in range(4)
        ]
        
        # Calculate winrate per quarter
        winrates = []
        for quarter in quarters:
            if not quarter:
                continue
            wins = sum(1 for t in quarter if t.result == "WIN")
            wr = wins / len(quarter)
            winrates.append(wr)
        
        if len(winrates) < 2:
            return 0.0
        
        # Calculate stability
        mean_wr = statistics.mean(winrates)
        std_wr = statistics.stdev(winrates)
        
        # ESI formula
        if mean_wr == 0:
            return 0.0
        
        esi = 1 - (std_wr / mean_wr)
        
        # Clamp between 0-1
        return max(0.0, min(1.0, esi))
    
    def calculate_pvs(self, 
                     total_trades: int,
                     winrate: float, 
                     profit_factor: float, 
                     max_drawdown: float) -> float:
        """
        Prop Verification Score: readiness for prop firm challenge.
        
        Checks:
        - Win rate >= 50%
        - Profit factor >= 1.5
        - Max drawdown <= 10%
        - Sample size >= 100 trades
        
        Returns:
            Float 0-1 (higher = more prop-ready)
        """
        
        # Component scores (weighted)
        wr_score = min(1.0, winrate / 50.0) if winrate > 0 else 0.0
        pf_score = min(1.0, profit_factor / 1.5) if profit_factor > 0 else 0.0
        dd_score = min(1.0, 10.0 / max_drawdown) if max_drawdown > 0 else 1.0
        size_score = min(1.0, total_trades / 100.0)
        
        # Weighted average
        pvs = (
            wr_score * 0.30 +
            pf_score * 0.30 +
            dd_score * 0.20 +
            size_score * 0.20
        )
        
        return round(pvs, 2)
    
    def calculate_sharpe_ratio(self, trades: List[EdgeLabTrade]) -> float:
        """
        Sharpe Ratio: risk-adjusted return metric.
        
        Formula: (Mean Return - Risk-Free Rate) / StdDev of Returns
        
        Assumes risk-free rate = 0 for simplicity
        """
        
        if len(trades) < 2:
            return 0.0
        
        returns = [t.profit_r for t in trades]
        
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        if std_return == 0:
            return 0.0
        
        sharpe = mean_return / std_return
        
        return round(sharpe, 2)


class PatternAnalyzer:
    """
    Detect trading patterns and performance variations.
    
    Analysis:
    - Best performing session (Tokyo/London/NY)
    - Best performing hour
    - Long vs Short edge
    """
    
    def __init__(self):
        pass
    
    def find_best_session(self, trades: List[EdgeLabTrade]) -> str:
        """
        Find which trading session has highest win rate.
        
        Returns:
            "Tokyo" | "London" | "NY" | "Unknown"
        """
        
        sessions = {}
        
        for trade in trades:
            session = trade.session if hasattr(trade, 'session') else "Unknown"
            
            if session not in sessions:
                sessions[session] = {'wins': 0, 'total': 0}
            
            sessions[session]['total'] += 1
            if trade.result == "WIN":
                sessions[session]['wins'] += 1
        
        # Calculate win rates
        best_session = "Unknown"
        best_wr = 0.0
        
        for session, data in sessions.items():
            if data['total'] == 0:
                continue
            wr = data['wins'] / data['total']
            if wr > best_wr:
                best_wr = wr
                best_session = session
        
        return best_session
    
    def find_best_hour(self, trades: List[EdgeLabTrade]) -> str:
        """
        Find which hour of day has highest win rate.
        
        Returns:
            "HH:00 UTC" format
        """
        
        hours = {}
        
        for trade in trades:
            hour = trade.timestamp_open.hour
            hour_str = f"{hour:02d}:00 UTC"
            
            if hour_str not in hours:
                hours[hour_str] = {'wins': 0, 'total': 0}
            
            hours[hour_str]['total'] += 1
            if trade.result == "WIN":
                hours[hour_str]['wins'] += 1
        
        # Find best hour
        best_hour = "Unknown"
        best_wr = 0.0
        
        for hour, data in hours.items():
            if data['total'] == 0:
                continue
            wr = data['wins'] / data['total']
            if wr > best_wr:
                best_wr = wr
                best_hour = hour
        
        return best_hour
    
    def calculate_directional_winrates(self, trades: List[EdgeLabTrade]) -> tuple:
        """
        Calculate win rate for LONG vs SHORT trades.
        
        Returns:
            (long_winrate, short_winrate) as percentages
        """
        
        longs = [t for t in trades if t.direction == "LONG"]
        shorts = [t for t in trades if t.direction == "SHORT"]
        
        long_wr = 0.0
        short_wr = 0.0
        
        if longs:
            long_wins = sum(1 for t in longs if t.result == "WIN")
            long_wr = (long_wins / len(longs)) * 100
        
        if shorts:
            short_wins = sum(1 for t in shorts if t.result == "WIN")
            short_wr = (short_wins / len(shorts)) * 100
        
        return long_wr, short_wr


class InsightGenerator:
    """
    Generate natural language recommendations from metrics.
    
    Provides actionable insights based on analysis results.
    """
    
    def __init__(self):
        pass
    
    def generate_recommendation(self,
                               winrate: float,
                               profit_factor: float,
                               esi: float,
                               pvs: float,
                               best_session: str) -> str:
        """
        Create actionable recommendation based on metrics.
        
        Args:
            winrate: Win rate percentage
            profit_factor: Profit factor
            esi: Edge Stability Index (0-1)
            pvs: Prop Verification Score (0-1)
            best_session: Best performing session
            
        Returns:
            Natural language recommendation string
        """
        
        insights = []
        
        # Overall edge assessment
        if winrate >= 55 and profit_factor >= 2.0:
            insights.append("Strong edge detected.")
        elif winrate >= 50 and profit_factor >= 1.5:
            insights.append("Profitable edge detected.")
        else:
            insights.append("Edge needs improvement.")
        
        # ESI assessment
        if esi >= 0.70:
            insights.append("Edge is stable over time.")
        elif esi >= 0.50:
            insights.append("Edge shows moderate consistency.")
        else:
            insights.append("Edge appears unstable - may be due to small sample or luck.")
        
        # PVS assessment
        if pvs >= 0.80:
            insights.append("Strategy is prop-firm ready.")
        elif pvs >= 0.60:
            insights.append("Close to prop-firm standards - minor improvements needed.")
        else:
            insights.append("Not yet ready for prop firm challenge.")
        
        # Session insight
        if best_session != "Unknown":
            insights.append(f"Best performance during {best_session} session - consider focusing trades here.")
        
        return " ".join(insights)