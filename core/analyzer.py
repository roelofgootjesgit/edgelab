"""
analyzer.py
===========

Performance analysis engine for EdgeLab.
Calculates trading metrics from QuantMetricsTrade objects.

Includes comprehensive pattern analysis and insights.

Author: QuantMetrics Development Team
Version: 2.3 (All template aliases - maximum compatibility)
"""

from typing import List, Dict, Any
import statistics
from core.quantmetrics_schema import QuantMetricsTrade, AnalysisResult
from core.pattern_analyzer import (
    TimingAnalyzer,
    DirectionalAnalyzer, 
    ExecutionAnalyzer,
    LossForensics,
    InsightGenerator
)


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
        self.advanced = AdvancedAnalyzer()
        self.timing = TimingAnalyzer()
        self.directional = DirectionalAnalyzer()
        self.execution = ExecutionAnalyzer()
        self.forensics = LossForensics()
        self.insights = InsightGenerator()
    
    def calculate(self, trades: List[QuantMetricsTrade]) -> Dict[str, Any]:
        """
        Calculate all metrics from trade list.
        
        Args:
            trades: List of QuantMetricsTrade objects
            
        Returns:
            Dictionary with comprehensive analysis results
            
        Raises:
            ValueError: If trades list is empty
        """
        
        if not trades:
            raise ValueError("Cannot analyze empty trade list")
        
        # Basic metrics
        basic_results = self._calculate_basic_metrics(trades)
        
        # Advanced metrics
        advanced_results = self.advanced.calculate_all(
            trades=trades,
            winrate=basic_results['win_rate'],
            profit_factor=basic_results['profit_factor'],
            max_drawdown=basic_results['max_drawdown_pct']
        )
        
        # Pattern analysis
        timing_results = self.timing.analyze(trades)
        directional_results = self.directional.analyze(trades)
        execution_results = self.execution.analyze(trades)
        forensics_results = self.forensics.analyze(trades)
        
        # Generate comprehensive insights
        insights_results = self.insights.generate(
            timing_results=timing_results,
            directional_results=directional_results,
            execution_results=execution_results,
            loss_results=forensics_results,
            basic_metrics={
                'win_rate': basic_results['win_rate'],
                'profit_factor': basic_results['profit_factor'],
                'expectancy': basic_results['expectancy']
            },
            trades=trades
        )
        
        # Combine all results
        return {
            **basic_results,
            **advanced_results,
            'timing_analysis': timing_results,
            'directional_analysis': directional_results,
            'execution_analysis': execution_results,
            'loss_forensics': forensics_results,
            'insights': insights_results
        }
    
    def _calculate_basic_metrics(self, trades: List[QuantMetricsTrade]) -> Dict[str, Any]:
        """Calculate fundamental metrics."""
        
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
        
        # Max Drawdown
        max_dd = self._calculate_max_drawdown(trades)
        
        # Return with COMPREHENSIVE ALIASES for maximum template compatibility
        return {
            # Trade counts
            'total_trades': total_trades,
            'wins': num_wins,
            'winning_trades': num_wins,  # Template alias
            'losses': num_losses,
            'losing_trades': num_losses,  # Template alias
            'timeouts': num_timeouts,
            
            # Win rate (multiple aliases)
            'win_rate': round(winrate, 2),
            'winrate': round(winrate, 2),  # Legacy alias
            
            # Profit metrics
            'profit_factor': round(profit_factor, 2),
            'expectancy': round(expectancy, 2),
            
            # Total profit
            'total_profit_r': round(total_profit, 2),
            'total_profit': round(total_profit, 2),  # Template alias
            
            # Gross profit/loss
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2),
            
            # Average win/loss (multiple aliases)
            'avg_win_r': round(avg_win, 2),
            'avg_win': round(avg_win, 2),  # Template alias
            'avg_loss_r': round(avg_loss, 2),
            'avg_loss': round(avg_loss, 2),  # Template alias
            
            # Drawdown (multiple aliases)
            'max_drawdown_pct': round(max_dd, 2),
            'max_drawdown': round(max_dd, 2)  # Template alias
        }
    
    def _calculate_max_drawdown(self, trades: List[QuantMetricsTrade]) -> float:
        """Calculate maximum drawdown percentage."""
        
        equity = [100.0]
        
        for trade in trades:
            change_pct = trade.profit_r * 1.0
            new_equity = equity[-1] * (1 + change_pct / 100)
            equity.append(new_equity)
        
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
    - ESI (Edge Stability Index)
    - PVS (Prop Verification Score)
    - Sharpe Ratio
    """
    
    def calculate_all(self, 
                     trades: List[QuantMetricsTrade],
                     winrate: float,
                     profit_factor: float,
                     max_drawdown: float) -> Dict[str, Any]:
        """Calculate all advanced metrics."""
        
        esi = self.calculate_esi(trades)
        pvs = self.calculate_pvs(len(trades), winrate, profit_factor, max_drawdown)
        sharpe = self.calculate_sharpe_ratio(trades)
        
        return {
            'esi': round(esi, 2),
            'pvs': round(pvs, 2),
            'sharpe_ratio': round(sharpe, 2)
        }
    
    def calculate_esi(self, trades: List[QuantMetricsTrade]) -> float:
        """Edge Stability Index: consistency measurement."""
        
        if len(trades) < 16:  # Need 4 per quarter
            return 0.0
        
        chunk_size = len(trades) // 4
        quarters = [trades[i*chunk_size:(i+1)*chunk_size] for i in range(4)]
        
        winrates = []
        for quarter in quarters:
            if not quarter:
                continue
            wins = sum(1 for t in quarter if t.result == "WIN")
            wr = wins / len(quarter)
            winrates.append(wr)
        
        if len(winrates) < 2:
            return 0.0
        
        mean_wr = statistics.mean(winrates)
        std_wr = statistics.stdev(winrates)
        
        if mean_wr == 0:
            return 0.0
        
        esi = 1 - (std_wr / mean_wr)
        return max(0.0, min(1.0, esi))
    
    def calculate_pvs(self, 
                     total_trades: int,
                     winrate: float, 
                     profit_factor: float, 
                     max_drawdown: float) -> float:
        """Prop Verification Score: prop firm readiness."""
        
        wr_score = min(1.0, winrate / 50.0) if winrate > 0 else 0.0
        pf_score = min(1.0, profit_factor / 1.5) if profit_factor > 0 else 0.0
        dd_score = min(1.0, 10.0 / max_drawdown) if max_drawdown > 0 else 1.0
        size_score = min(1.0, total_trades / 100.0)
        
        pvs = (
            wr_score * 0.30 +
            pf_score * 0.30 +
            dd_score * 0.20 +
            size_score * 0.20
        )
        
        return pvs
    
    def calculate_sharpe_ratio(self, trades: List[QuantMetricsTrade]) -> float:
        """Sharpe Ratio: risk-adjusted returns."""
        
        if len(trades) < 2:
            return 0.0
        
        returns = [t.profit_r for t in trades]
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        if std_return == 0:
            return 0.0
        
        return mean_return / std_return