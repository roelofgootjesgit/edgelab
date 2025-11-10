"""
pattern_analyzer.py
==================

Pattern detection and analysis for trading strategies.
Identifies timing patterns, directional bias, execution quality, and loss causes.

Author: EdgeLab Development Team
Version: 1.3
"""

from typing import List, Dict
from core.edgelab_schema import EdgeLabTrade
from datetime import datetime


class TimingAnalyzer:
    """
    Analyze performance by time (session, hour, day)
    Detect when strategy works best
    """
    
    def analyze(self, trades: List[EdgeLabTrade]) -> Dict:
        """
        Analyze timing patterns in trades
        
        Args:
            trades: List of EdgeLabTrade objects
            
        Returns:
            Dict with session_breakdown, hourly_breakdown, best_hour
        """
        
        session_breakdown = self._analyze_sessions(trades)
        hourly_breakdown = self._analyze_hours(trades)
        best_hour = self._find_best_hour(hourly_breakdown)
        
        return {
            'session_breakdown': session_breakdown,
            'hourly_breakdown': hourly_breakdown,
            'best_hour': best_hour
        }
    
    def _analyze_sessions(self, trades: List[EdgeLabTrade]) -> Dict:
        """Analyze performance by trading session"""
        
        sessions = {
            'Tokyo': {'trades': [], 'range': '00:00-08:00 UTC'},
            'London': {'trades': [], 'range': '08:00-16:00 UTC'},
            'NY': {'trades': [], 'range': '14:00-22:00 UTC'}
        }
        
        # Group trades by session
        for trade in trades:
            hour = trade.timestamp_open.hour
            
            if 0 <= hour < 8:
                sessions['Tokyo']['trades'].append(trade)
            if 8 <= hour < 16:
                sessions['London']['trades'].append(trade)
            if 14 <= hour < 22:
                sessions['NY']['trades'].append(trade)
        
        # Calculate metrics per session
        results = {}
        for session_name, data in sessions.items():
            session_trades = data['trades']
            
            if not session_trades:
                results[session_name] = {
                    'total_trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'winrate': 0.0,
                    'expectancy': 0.0,
                    'verdict': 'NO_DATA',
                    'time_range': data['range']
                }
                continue
            
            wins = len([t for t in session_trades if t.result == 'WIN'])
            losses = len([t for t in session_trades if t.result == 'LOSS'])
            winrate = (wins / len(session_trades)) * 100
            
            total_profit_r = sum(t.profit_r for t in session_trades)
            expectancy = total_profit_r / len(session_trades)
            
            # Determine verdict
            if expectancy > 0.5 and winrate >= 55:
                verdict = 'FOCUS'
            elif expectancy > 0 and winrate >= 45:
                verdict = 'NEUTRAL'
            else:
                verdict = 'AVOID'
            
            results[session_name] = {
                'total_trades': len(session_trades),
                'wins': wins,
                'losses': losses,
                'winrate': round(winrate, 1),
                'expectancy': round(expectancy, 2),
                'verdict': verdict,
                'time_range': data['range']
            }
        
        return results
    
    def _analyze_hours(self, trades: List[EdgeLabTrade]) -> Dict:
        """Analyze performance by hour of day"""
        
        hourly_stats = {}
        
        for trade in trades:
            hour = trade.timestamp_open.hour
            
            if hour not in hourly_stats:
                hourly_stats[hour] = []
            
            hourly_stats[hour].append(trade)
        
        # Calculate metrics per hour
        results = {}
        for hour, hour_trades in hourly_stats.items():
            wins = len([t for t in hour_trades if t.result == 'WIN'])
            winrate = (wins / len(hour_trades)) * 100
            
            total_profit_r = sum(t.profit_r for t in hour_trades)
            expectancy = total_profit_r / len(hour_trades)
            
            results[hour] = {
                'total_trades': len(hour_trades),
                'wins': wins,
                'winrate': round(winrate, 1),
                'expectancy': round(expectancy, 2)
            }
        
        return results
    
    def _find_best_hour(self, hourly_breakdown: Dict) -> Dict:
        """Find hour with best performance"""
        
        if not hourly_breakdown:
            return {'hour': None, 'winrate': 0.0, 'expectancy': 0.0}
        
        best_hour = None
        best_expectancy = -999
        
        for hour, stats in hourly_breakdown.items():
            if stats['expectancy'] > best_expectancy and stats['total_trades'] >= 2:
                best_expectancy = stats['expectancy']
                best_hour = hour
        
        if best_hour is None:
            return {'hour': None, 'winrate': 0.0, 'expectancy': 0.0}
        
        return {
            'hour': best_hour,
            'winrate': hourly_breakdown[best_hour]['winrate'],
            'expectancy': hourly_breakdown[best_hour]['expectancy'],
            'total_trades': hourly_breakdown[best_hour]['total_trades']
        }


class DirectionalAnalyzer:
    """
    Analyze LONG vs SHORT performance
    Detect directional bias and edge
    """
    
    def analyze(self, trades: List[EdgeLabTrade]) -> Dict:
        """
        Compare LONG vs SHORT performance
        
        Returns:
            {
                'long_stats': {...},
                'short_stats': {...},
                'bias': 'LONG'|'SHORT'|'NEUTRAL',
                'recommendation': str,
                'expected_improvement': float
            }
        """
        
        # Separate by direction
        longs = [t for t in trades if t.direction == 'LONG']
        shorts = [t for t in trades if t.direction == 'SHORT']
        
        # Calculate metrics for each
        long_stats = self._calculate_direction_metrics(longs, 'LONG')
        short_stats = self._calculate_direction_metrics(shorts, 'SHORT')
        
        # Determine bias
        bias = self._determine_bias(long_stats, short_stats)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(long_stats, short_stats, bias)
        
        # Calculate expected improvement
        expected_improvement = self._calculate_improvement(
            trades, longs, shorts, bias
        )
        
        return {
            'long_stats': long_stats,
            'short_stats': short_stats,
            'bias': bias,
            'recommendation': recommendation,
            'expected_improvement': expected_improvement
        }
    
    def _calculate_direction_metrics(self, trades: List[EdgeLabTrade], direction: str) -> Dict:
        """Calculate metrics for one direction"""
        if not trades:
            return {
                'direction': direction,
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'winrate': 0.0,
                'expectancy': 0.0,
                'total_profit_r': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'edge': 'NONE'
            }
        
        wins = [t for t in trades if t.result == 'WIN']
        losses = [t for t in trades if t.result == 'LOSS']
        
        winrate = (len(wins) / len(trades)) * 100 if trades else 0
        
        total_profit_r = sum(t.profit_r for t in trades)
        expectancy = total_profit_r / len(trades) if trades else 0
        
        avg_win = sum(t.profit_r for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.profit_r for t in losses) / len(losses) if losses else 0
        
        # Determine edge strength
        if expectancy > 0.5 and winrate >= 50:
            edge = 'STRONG'
        elif expectancy > 0 and winrate >= 45:
            edge = 'WEAK'
        else:
            edge = 'NONE'
        
        return {
            'direction': direction,
            'total_trades': len(trades),
            'wins': len(wins),
            'losses': len(losses),
            'winrate': round(winrate, 1),
            'expectancy': round(expectancy, 2),
            'total_profit_r': round(total_profit_r, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'edge': edge
        }
    
    def _determine_bias(self, long_stats: Dict, short_stats: Dict) -> str:
        """Determine which direction has better edge"""
        
        # No trades in one direction
        if long_stats['total_trades'] == 0:
            return 'SHORT'
        if short_stats['total_trades'] == 0:
            return 'LONG'
        
        # Compare expectancy
        long_exp = long_stats['expectancy']
        short_exp = short_stats['expectancy']
        
        # Clear bias if difference > 0.3R
        if long_exp - short_exp > 0.3:
            return 'LONG'
        elif short_exp - long_exp > 0.3:
            return 'SHORT'
        else:
            return 'NEUTRAL'
    
    def _generate_recommendation(self, long_stats: Dict, short_stats: Dict, bias: str) -> str:
        """Generate actionable recommendation"""
        
        if bias == 'LONG':
            return (f"Focus exclusively on LONG trades. "
                   f"LONG expectancy ({long_stats['expectancy']}R) significantly "
                   f"outperforms SHORT ({short_stats['expectancy']}R).")
        
        elif bias == 'SHORT':
            return (f"Focus exclusively on SHORT trades. "
                   f"SHORT expectancy ({short_stats['expectancy']}R) significantly "
                   f"outperforms LONG ({long_stats['expectancy']}R).")
        
        else:
            return (f"No clear directional bias detected. "
                   f"Both LONG ({long_stats['expectancy']}R) and "
                   f"SHORT ({short_stats['expectancy']}R) show similar edge.")
    
    def _calculate_improvement(self, all_trades: List[EdgeLabTrade], 
                               longs: List[EdgeLabTrade], 
                               shorts: List[EdgeLabTrade],
                               bias: str) -> float:
        """Calculate expected WR improvement if following bias"""
        
        if bias == 'NEUTRAL' or not all_trades:
            return 0.0
        
        # Current WR
        current_wins = len([t for t in all_trades if t.result == 'WIN'])
        current_wr = (current_wins / len(all_trades)) * 100
        
        # WR if following bias
        if bias == 'LONG':
            focused_wins = len([t for t in longs if t.result == 'WIN'])
            focused_wr = (focused_wins / len(longs)) * 100 if longs else 0
        else:
            focused_wins = len([t for t in shorts if t.result == 'WIN'])
            focused_wr = (focused_wins / len(shorts)) * 100 if shorts else 0
        
        improvement = focused_wr - current_wr
        return round(improvement, 1)


class ExecutionAnalyzer:
    """
    Analyze trade execution quality
    Detect discipline issues and exit timing problems
    """
    
    def analyze(self, trades: List[EdgeLabTrade]) -> Dict:
        """
        Analyze execution quality
        
        Returns:
            {
                'tp_behavior': {...},
                'sl_behavior': {...},
                'duration_analysis': {...},
                'execution_score': int,
                'issues': List[str],
                'recommendations': List[str]
            }
        """
        
        tp_behavior = self._analyze_tp_behavior(trades)
        sl_behavior = self._analyze_sl_behavior(trades)
        duration_analysis = self._analyze_duration(trades)
        
        # Calculate overall execution score
        execution_score = self._calculate_execution_score(
            tp_behavior, sl_behavior, duration_analysis
        )
        
        # Identify issues
        issues = self._identify_issues(tp_behavior, sl_behavior)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            tp_behavior, sl_behavior, duration_analysis
        )
        
        return {
            'tp_behavior': tp_behavior,
            'sl_behavior': sl_behavior,
            'duration_analysis': duration_analysis,
            'execution_score': execution_score,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _analyze_tp_behavior(self, trades: List[EdgeLabTrade]) -> Dict:
        """Analyze take profit behavior"""
        
        winning_trades = [t for t in trades if t.result == 'WIN']
        
        if not winning_trades:
            return {
                'total_wins': 0,
                'full_tp_hits': 0,
                'early_exits': 0,
                'full_tp_pct': 0.0,
                'estimated_missed_profit': 0.0
            }
        
        # Detect full TP vs early exits
        full_tp_hits = []
        early_exits = []
        
        for trade in winning_trades:
            # Calculate theoretical max R (if hit TP)
            if trade.direction == 'LONG':
                risk = trade.entry_price - trade.sl
                reward = trade.tp - trade.entry_price
            else:
                risk = trade.sl - trade.entry_price
                reward = trade.entry_price - trade.tp
            
            theoretical_r = reward / risk if risk > 0 else 0
            
            # If achieved R is close to theoretical, it's a full TP
            if abs(trade.profit_r - theoretical_r) < 0.2:
                full_tp_hits.append(trade)
            else:
                early_exits.append(trade)
        
        # Estimate missed profit from early exits
        missed_profit = 0.0
        for trade in early_exits:
            # Calculate how much more could have been made
            if trade.direction == 'LONG':
                risk = trade.entry_price - trade.sl
                reward = trade.tp - trade.entry_price
            else:
                risk = trade.sl - trade.entry_price
                reward = trade.entry_price - trade.tp
            
            theoretical_r = reward / risk if risk > 0 else 0
            missed_r = theoretical_r - trade.profit_r
            missed_profit += missed_r
        
        return {
            'total_wins': len(winning_trades),
            'full_tp_hits': len(full_tp_hits),
            'early_exits': len(early_exits),
            'full_tp_pct': round((len(full_tp_hits) / len(winning_trades)) * 100, 1),
            'estimated_missed_profit': round(missed_profit, 2)
        }
    
    def _analyze_sl_behavior(self, trades: List[EdgeLabTrade]) -> Dict:
        """Analyze stop loss behavior"""
        
        losing_trades = [t for t in trades if t.result == 'LOSS']
        
        if not losing_trades:
            return {
                'total_losses': 0,
                'proper_sl_hits': 0,
                'held_past_sl': 0,
                'proper_sl_pct': 100.0,
                'extra_loss_cost': 0.0
            }
        
        # Detect proper SL vs held past SL
        proper_sl = []
        held_past_sl = []
        
        for trade in losing_trades:
            # Expected loss = -1R (if SL respected)
            # If loss > -1.5R, likely held past SL
            if trade.profit_r >= -1.2:
                proper_sl.append(trade)
            else:
                held_past_sl.append(trade)
        
        # Calculate extra cost from holding past SL
        extra_cost = 0.0
        for trade in held_past_sl:
            # Extra loss = actual loss - expected (-1R)
            extra_loss = abs(trade.profit_r) - 1.0
            extra_cost += extra_loss
        
        return {
            'total_losses': len(losing_trades),
            'proper_sl_hits': len(proper_sl),
            'held_past_sl': len(held_past_sl),
            'proper_sl_pct': round((len(proper_sl) / len(losing_trades)) * 100, 1),
            'extra_loss_cost': round(extra_cost, 2)
        }
    
    def _analyze_duration(self, trades: List[EdgeLabTrade]) -> Dict:
        """Analyze trade duration patterns"""
        
        duration_groups = {
            'quick': [],      # < 1 hour
            'medium': [],     # 1-4 hours
            'long': []        # > 4 hours
        }
        
        for trade in trades:
            duration = (trade.timestamp_close - trade.timestamp_open).total_seconds() / 3600
            
            if duration < 1:
                duration_groups['quick'].append(trade)
            elif duration <= 4:
                duration_groups['medium'].append(trade)
            else:
                duration_groups['long'].append(trade)
        
        # Calculate metrics per group
        results = {}
        for group_name, group_trades in duration_groups.items():
            if not group_trades:
                results[group_name] = {
                    'total_trades': 0,
                    'wins': 0,
                    'winrate': 0.0,
                    'expectancy': 0.0
                }
                continue
            
            wins = len([t for t in group_trades if t.result == 'WIN'])
            winrate = (wins / len(group_trades)) * 100
            expectancy = sum(t.profit_r for t in group_trades) / len(group_trades)
            
            results[group_name] = {
                'total_trades': len(group_trades),
                'wins': wins,
                'winrate': round(winrate, 1),
                'expectancy': round(expectancy, 2)
            }
        
        # Determine optimal duration
        best_group = max(results.items(), 
                        key=lambda x: x[1]['expectancy'] if x[1]['total_trades'] > 0 else -999)
        
        return {
            'breakdown': results,
            'optimal_duration': best_group[0]
        }
    
    def _calculate_execution_score(self, tp_behavior: Dict, sl_behavior: Dict, 
                                   duration_analysis: Dict) -> int:
        """Calculate overall execution quality (0-100)"""
        
        # TP discipline (40% weight)
        tp_score = tp_behavior['full_tp_pct'] * 0.4
        
        # SL discipline (40% weight)
        sl_score = sl_behavior['proper_sl_pct'] * 0.4
        
        # Duration optimization (20% weight)
        optimal = duration_analysis['optimal_duration']
        duration_wr = duration_analysis['breakdown'][optimal]['winrate']
        duration_score = 20 if duration_wr >= 50 else 10
        
        total_score = int(tp_score + sl_score + duration_score)
        
        return min(100, max(0, total_score))
    
    def _identify_issues(self, tp_behavior: Dict, sl_behavior: Dict) -> List[str]:
        """Identify execution problems"""
        
        issues = []
        
        # Early exit problem
        if tp_behavior['early_exits'] > 0:
            pct = (tp_behavior['early_exits'] / tp_behavior['total_wins']) * 100
            missed = tp_behavior['estimated_missed_profit']
            issues.append(
                f"Early exits: {tp_behavior['early_exits']} trades ({pct:.0f}%) "
                f"cost ~{missed:.1f}R profit"
            )
        
        # SL violation problem
        if sl_behavior['held_past_sl'] > 0:
            pct = (sl_behavior['held_past_sl'] / sl_behavior['total_losses']) * 100
            cost = sl_behavior['extra_loss_cost']
            issues.append(
                f"Held past SL: {sl_behavior['held_past_sl']} trades ({pct:.0f}%) "
                f"cost {cost:.1f}R extra loss"
            )
        
        return issues
    
    def _generate_recommendations(self, tp_behavior: Dict, sl_behavior: Dict,
                                 duration_analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # TP recommendation
        if tp_behavior['full_tp_pct'] < 70:
            recommendations.append(
                "Trust your targets - let winners run to full TP. "
                f"Estimated gain: +{tp_behavior['estimated_missed_profit']:.1f}R"
            )
        
        # SL recommendation
        if sl_behavior['proper_sl_pct'] < 90:
            recommendations.append(
                "NEVER hold past stop loss. "
                f"Following this rule saves {sl_behavior['extra_loss_cost']:.1f}R"
            )
        
        # Duration recommendation
        optimal = duration_analysis['optimal_duration']
        optimal_stats = duration_analysis['breakdown'][optimal]
        
        if optimal == 'quick':
            recommendations.append(
                f"Your edge works best in quick trades (<1h). "
                f"Consider scalping approach. WR: {optimal_stats['winrate']}%"
            )
        elif optimal == 'medium':
            recommendations.append(
                f"Optimal hold time: 1-4 hours. "
                f"Consider closing if no clear profit after 4h. WR: {optimal_stats['winrate']}%"
            )
        else:
            recommendations.append(
                f"Your edge needs time (>4h holds best). "
                f"Be patient, let trades develop. WR: {optimal_stats['winrate']}%"
            )
        
        return recommendations


class LossForensics:
    """
    Deep dive into why trades fail
    Categorize loss types and identify root causes
    """
    
    def analyze(self, trades: List[EdgeLabTrade]) -> Dict:
        """
        Analyze losing trades in detail
        
        Returns:
            {
                'loss_breakdown': {...},
                'loss_causes': {...},
                'emotional_trades': {...},
                'preventable_cost': float,
                'critical_finding': str
            }
        """
        
        losses = [t for t in trades if t.result == 'LOSS']
        
        if not losses:
            return {
                'loss_breakdown': {},
                'loss_causes': {},
                'emotional_trades': {},
                'preventable_cost': 0.0,
                'critical_finding': 'No losses to analyze'
            }
        
        # Categorize losses
        loss_breakdown = self._categorize_losses(losses)
        
        # Identify root causes
        loss_causes = self._identify_causes(losses, trades)
        
        # Detect emotional/revenge trading
        emotional_trades = self._detect_emotional_trades(trades)
        
        # Calculate preventable cost
        preventable_cost = self._calculate_preventable_cost(loss_breakdown, emotional_trades)
        
        # Generate critical finding
        critical_finding = self._generate_critical_finding(
            loss_breakdown, loss_causes, emotional_trades
        )
        
        return {
            'loss_breakdown': loss_breakdown,
            'loss_causes': loss_causes,
            'emotional_trades': emotional_trades,
            'preventable_cost': preventable_cost,
            'critical_finding': critical_finding
        }
    
    def _categorize_losses(self, losses: List[EdgeLabTrade]) -> Dict:
        """Categorize losses by type"""
        
        proper_losses = []      # Expected losses (SL hit correctly)
        early_exits = []        # Exited before SL (panic)
        held_past_sl = []       # Held past SL (hope)
        
        for trade in losses:
            # Expected loss = -1R
            if -1.2 <= trade.profit_r <= -0.8:
                proper_losses.append(trade)
            elif trade.profit_r > -0.8:
                # Less than -1R = early exit (panic)
                early_exits.append(trade)
            else:
                # More than -1R = held past SL
                held_past_sl.append(trade)
        
        # Calculate costs
        proper_cost = sum(abs(t.profit_r) for t in proper_losses)
        early_cost = sum(abs(t.profit_r) for t in early_exits)
        held_cost = sum(abs(t.profit_r) for t in held_past_sl)
        
        # Calculate what SHOULD have been if rules followed
        early_should_have = len(early_exits) * 1.0  # Should be -1R each
        early_actual = sum(abs(t.profit_r) for t in early_exits)
        early_difference = early_actual - early_should_have
        
        held_should_have = len(held_past_sl) * 1.0
        held_actual = sum(abs(t.profit_r) for t in held_past_sl)
        held_extra_cost = held_actual - held_should_have
        
        return {
            'proper': {
                'count': len(proper_losses),
                'avg_loss': round(proper_cost / len(proper_losses), 2) if proper_losses else 0,
                'total_cost': round(proper_cost, 2),
                'verdict': 'EXPECTED'
            },
            'early_exits': {
                'count': len(early_exits),
                'avg_loss': round(early_cost / len(early_exits), 2) if early_exits else 0,
                'total_cost': round(early_cost, 2),
                'extra_cost': round(early_difference, 2),
                'verdict': 'PANIC'
            },
            'held_past_sl': {
                'count': len(held_past_sl),
                'avg_loss': round(held_cost / len(held_past_sl), 2) if held_past_sl else 0,
                'total_cost': round(held_cost, 2),
                'extra_cost': round(held_extra_cost, 2),
                'verdict': 'HOPE'
            }
        }
    
    def _identify_causes(self, losses: List[EdgeLabTrade], all_trades: List[EdgeLabTrade]) -> Dict:
        """Identify why losses occurred"""
        
        causes = {
            'wrong_direction': 0,
            'poor_timing': 0,
            'wrong_session': 0,
            'other': 0
        }
        
        # Analyze each loss
        for loss in losses:
            # Check if direction was the problem
            direction_losses = [t for t in losses if t.direction == loss.direction]
            direction_wins = [t for t in all_trades 
                            if t.direction == loss.direction and t.result == 'WIN']
            
            if len(direction_losses) > len(direction_wins):
                causes['wrong_direction'] += 1
                continue
            
            # Check if session was the problem
            session_losses = [t for t in losses if t.session == loss.session]
            session_wins = [t for t in all_trades 
                          if t.session == loss.session and t.result == 'WIN']
            
            if len(session_losses) > len(session_wins) * 1.5:
                causes['wrong_session'] += 1
                continue
            
            # Check if timing within session
            hour = loss.timestamp_open.hour
            hour_losses = [t for t in losses if t.timestamp_open.hour == hour]
            
            if len(hour_losses) >= 2:
                causes['poor_timing'] += 1
                continue
            
            causes['other'] += 1
        
        # Convert to percentages
        total = len(losses)
        return {
            'wrong_direction': {
                'count': causes['wrong_direction'],
                'percentage': round((causes['wrong_direction'] / total) * 100, 1)
            },
            'poor_timing': {
                'count': causes['poor_timing'],
                'percentage': round((causes['poor_timing'] / total) * 100, 1)
            },
            'wrong_session': {
                'count': causes['wrong_session'],
                'percentage': round((causes['wrong_session'] / total) * 100, 1)
            },
            'other': {
                'count': causes['other'],
                'percentage': round((causes['other'] / total) * 100, 1)
            }
        }
    
    def _detect_emotional_trades(self, trades: List[EdgeLabTrade]) -> Dict:
        """Detect revenge trading and emotional decisions"""
        
        emotional_trades = []
        
        # Sort by time
        sorted_trades = sorted(trades, key=lambda t: t.timestamp_open)
        
        for i in range(1, len(sorted_trades)):
            prev_trade = sorted_trades[i-1]
            current_trade = sorted_trades[i]
            
            # Check if current trade is within 30 min of previous loss
            if prev_trade.result == 'LOSS':
                time_diff = (current_trade.timestamp_open - prev_trade.timestamp_close).total_seconds() / 60
                
                if time_diff < 30:
                    emotional_trades.append({
                        'trade': current_trade,
                        'time_after_loss': round(time_diff, 1),
                        'result': current_trade.result
                    })
        
        # Calculate statistics
        if not emotional_trades:
            return {
                'count': 0,
                'win_count': 0,
                'loss_count': 0,
                'winrate': 0.0,
                'cost': 0.0,
                'verdict': 'NONE'
            }
        
        wins = len([t for t in emotional_trades if t['result'] == 'WIN'])
        losses = len([t for t in emotional_trades if t['result'] == 'LOSS'])
        winrate = (wins / len(emotional_trades)) * 100
        
        cost = sum(abs(t['trade'].profit_r) for t in emotional_trades if t['result'] == 'LOSS')
        
        return {
            'count': len(emotional_trades),
            'win_count': wins,
            'loss_count': losses,
            'winrate': round(winrate, 1),
            'cost': round(cost, 2),
            'verdict': 'REVENGE_TRADING' if len(emotional_trades) > 0 else 'NONE'
        }
    
    def _calculate_preventable_cost(self, loss_breakdown: Dict, emotional_trades: Dict) -> float:
        """Calculate total cost of preventable losses"""
        
        preventable = 0.0
        
        # Early exits cost
        if 'early_exits' in loss_breakdown:
            preventable += loss_breakdown['early_exits'].get('extra_cost', 0)
        
        # Held past SL cost
        if 'held_past_sl' in loss_breakdown:
            preventable += loss_breakdown['held_past_sl'].get('extra_cost', 0)
        
        # Emotional trading cost
        preventable += emotional_trades.get('cost', 0)
        
        return round(preventable, 2)
    
    def _generate_critical_finding(self, loss_breakdown: Dict, loss_causes: Dict, 
                                   emotional_trades: Dict) -> str:
        """Generate the most important finding"""
        
        findings = []
        
        # Check for held past SL issue
        held = loss_breakdown.get('held_past_sl', {})
        if held.get('count', 0) > 0:
            findings.append({
                'severity': held['count'] * held.get('extra_cost', 0),
                'message': f"Held past SL {held['count']} times costing {held.get('extra_cost', 0):.1f}R extra"
            })
        
        # Check for wrong session issue
        wrong_session = loss_causes.get('wrong_session', {})
        if wrong_session.get('percentage', 0) > 30:
            findings.append({
                'severity': wrong_session['count'],
                'message': f"{wrong_session['percentage']:.0f}% of losses from wrong session trading"
            })
        
        # Check for emotional trading
        if emotional_trades.get('count', 0) > 0:
            findings.append({
                'severity': emotional_trades.get('cost', 0),
                'message': f"{emotional_trades['count']} revenge trades cost {emotional_trades.get('cost', 0):.1f}R"
            })
        
        # Check for wrong direction
        wrong_dir = loss_causes.get('wrong_direction', {})
        if wrong_dir.get('percentage', 0) > 40:
            findings.append({
                'severity': wrong_dir['count'],
                'message': f"{wrong_dir['percentage']:.0f}% of losses from wrong directional bias"
            })
        
        if not findings:
            return "Losses appear to be proper risk management (SL hits)"
        
        # Return most severe finding
        critical = max(findings, key=lambda x: x['severity'])
        return critical['message']