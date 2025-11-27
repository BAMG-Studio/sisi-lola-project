"""
Analytics Aggregation Dashboard
Collect and visualize metrics from all platforms
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import csv


@dataclass
class PlatformMetrics:
    """Daily metrics for a platform"""
    platform: str
    date: str
    followers: int = 0
    posts_count: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_count: int = 0  # likes + comments + shares
    engagement_rate: float = 0.0
    profile_visits: int = 0
    clicks: int = 0
    video_views: int = 0
    watch_time_minutes: int = 0
    new_followers: int = 0
    notes: str = ""


class AnalyticsDashboard:
    """Aggregate analytics from all platforms"""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            base_path = Path(__file__).parent.parent
            db_path = base_path / "05_BRANDING_ARTIFACTS" / "sisi_lola_analytics.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()
    
    def initialize_database(self):
        """Create analytics database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Daily metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                date TEXT NOT NULL,
                followers INTEGER DEFAULT 0,
                posts_count INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                engagement_count INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                profile_visits INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                video_views INTEGER DEFAULT 0,
                watch_time_minutes INTEGER DEFAULT 0,
                new_followers INTEGER DEFAULT 0,
                notes TEXT,
                UNIQUE(platform, date)
            )
        ''')
        
        # Post-level metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                post_id TEXT NOT NULL,
                post_date TEXT NOT NULL,
                post_type TEXT,
                content_type TEXT,
                caption TEXT,
                impressions INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                saves INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                video_views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                UNIQUE(platform, post_id)
            )
        ''')
        
        # Monetization tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monetization_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                date TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                target_value REAL NOT NULL,
                percentage_complete REAL DEFAULT 0.0,
                UNIQUE(platform, date, metric_name)
            )
        ''')
        
        # Growth milestones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                milestone_type TEXT NOT NULL,
                milestone_value INTEGER NOT NULL,
                achieved_date TEXT,
                days_to_achieve INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_daily_metrics(self, metrics: PlatformMetrics) -> bool:
        """Add or update daily metrics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_metrics (
                    platform, date, followers, posts_count, impressions, reach,
                    engagement_count, engagement_rate, profile_visits, clicks,
                    video_views, watch_time_minutes, new_followers, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.platform, metrics.date, metrics.followers, metrics.posts_count,
                metrics.impressions, metrics.reach, metrics.engagement_count,
                metrics.engagement_rate, metrics.profile_visits, metrics.clicks,
                metrics.video_views, metrics.watch_time_minutes, metrics.new_followers,
                metrics.notes
            ))
            
            conn.commit()
            success = True
        except Exception as e:
            print(f"Error adding metrics: {e}")
            success = False
        finally:
            conn.close()
        
        return success
    
    def get_platform_metrics(self, platform: str, days: int = 30) -> List[Dict]:
        """Get metrics for a platform over specified days"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM daily_metrics
            WHERE platform = ? AND date >= ?
            ORDER BY date DESC
        ''', (platform, start_date))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_all_platforms_summary(self, date: str = None) -> Dict:
        """Get summary metrics for all platforms on a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_metrics
            WHERE date = ?
            ORDER BY platform
        ''', (date,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Calculate totals
        total_followers = sum(r['followers'] for r in results)
        total_engagement = sum(r['engagement_count'] for r in results)
        total_impressions = sum(r['impressions'] for r in results)
        
        avg_engagement_rate = (
            sum(r['engagement_rate'] for r in results) / len(results)
            if results else 0.0
        )
        
        return {
            'date': date,
            'total_followers': total_followers,
            'total_engagement': total_engagement,
            'total_impressions': total_impressions,
            'avg_engagement_rate': avg_engagement_rate,
            'by_platform': results
        }
    
    def get_growth_trends(self, platform: str, days: int = 30) -> Dict:
        """Calculate growth trends for a platform"""
        metrics = self.get_platform_metrics(platform, days)
        
        if len(metrics) < 2:
            return {
                'platform': platform,
                'days_analyzed': len(metrics),
                'follower_growth': 0,
                'avg_daily_growth': 0,
                'trend': 'insufficient_data'
            }
        
        # Sort by date ascending
        metrics.sort(key=lambda x: x['date'])
        
        start_followers = metrics[0]['followers']
        end_followers = metrics[-1]['followers']
        
        follower_growth = end_followers - start_followers
        days_actual = len(metrics)
        avg_daily_growth = follower_growth / days_actual if days_actual > 0 else 0
        
        # Determine trend
        if follower_growth > 0:
            trend = 'growing'
        elif follower_growth < 0:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'platform': platform,
            'days_analyzed': days_actual,
            'start_followers': start_followers,
            'end_followers': end_followers,
            'follower_growth': follower_growth,
            'avg_daily_growth': avg_daily_growth,
            'growth_percentage': (follower_growth / start_followers * 100) if start_followers > 0 else 0,
            'trend': trend
        }
    
    def update_monetization_progress(self, platform: str, metric_name: str,
                                    current_value: float, target_value: float):
        """Update progress toward monetization requirements"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        date = datetime.now().strftime('%Y-%m-%d')
        percentage = (current_value / target_value * 100) if target_value > 0 else 0
        
        cursor.execute('''
            INSERT OR REPLACE INTO monetization_tracking (
                platform, date, metric_name, metric_value, target_value, percentage_complete
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (platform, date, metric_name, current_value, target_value, percentage))
        
        conn.commit()
        conn.close()
    
    def get_monetization_status(self) -> Dict:
        """Get current monetization status for all platforms"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get latest entry for each platform/metric
        cursor.execute('''
            SELECT platform, metric_name, metric_value, target_value, 
                   percentage_complete, date
            FROM monetization_tracking
            WHERE date = (
                SELECT MAX(date) FROM monetization_tracking t2
                WHERE t2.platform = monetization_tracking.platform
                AND t2.metric_name = monetization_tracking.metric_name
            )
            ORDER BY platform, metric_name
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Group by platform
        by_platform = {}
        for row in results:
            platform = row['platform']
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append({
                'metric': row['metric_name'],
                'current': row['metric_value'],
                'target': row['target_value'],
                'percentage': row['percentage_complete']
            })
        
        return by_platform
    
    def record_milestone(self, platform: str, milestone_type: str,
                        milestone_value: int, start_date: str = None):
        """Record achievement of a milestone"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        achieved_date = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate days to achieve if start date provided
        days_to_achieve = None
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.now()
            days_to_achieve = (end - start).days
        
        cursor.execute('''
            INSERT INTO milestones (platform, milestone_type, milestone_value, 
                                   achieved_date, days_to_achieve)
            VALUES (?, ?, ?, ?, ?)
        ''', (platform, milestone_type, milestone_value, achieved_date, days_to_achieve))
        
        conn.commit()
        conn.close()
    
    def export_to_csv(self, output_dir: Path = None):
        """Export analytics to CSV files"""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "08_MLOPS_PIPELINE" / "reports"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        
        # Export daily metrics
        df = conn.execute('SELECT * FROM daily_metrics ORDER BY date DESC, platform')
        with open(output_dir / 'daily_metrics.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in df.description])
            writer.writerows(df.fetchall())
        
        # Export monetization tracking
        df = conn.execute('SELECT * FROM monetization_tracking ORDER BY date DESC')
        with open(output_dir / 'monetization_tracking.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in df.description])
            writer.writerows(df.fetchall())
        
        conn.close()
        
        return output_dir
    
    def generate_dashboard_report(self) -> str:
        """Generate comprehensive dashboard report"""
        summary = self.get_all_platforms_summary()
        
        report = []
        report.append("=" * 70)
        report.append("SISI LOLA ANALYTICS DASHBOARD")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("OVERALL SUMMARY:")
        report.append(f"  Total Followers: {summary['total_followers']:,}")
        report.append(f"  Total Engagement: {summary['total_engagement']:,}")
        report.append(f"  Total Impressions: {summary['total_impressions']:,}")
        report.append(f"  Avg Engagement Rate: {summary['avg_engagement_rate']:.2f}%")
        report.append("")
        
        report.append("BY PLATFORM:")
        report.append("-" * 70)
        
        platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitch', 
                    'Vumistream', 'Twiva']
        
        for platform in platforms:
            # Get 30-day trends
            trends = self.get_growth_trends(platform, 30)
            
            report.append(f"\n{platform}:")
            report.append(f"  Followers: {trends.get('end_followers', 0):,}")
            report.append(f"  30-Day Growth: {trends.get('follower_growth', 0):,} "
                         f"({trends.get('growth_percentage', 0):.1f}%)")
            report.append(f"  Avg Daily Growth: {trends.get('avg_daily_growth', 0):.1f}")
            report.append(f"  Trend: {trends.get('trend', 'N/A')}")
        
        report.append("")
        report.append("=" * 70)
        report.append("MONETIZATION PROGRESS:")
        report.append("=" * 70)
        
        monetization = self.get_monetization_status()
        
        for platform, metrics in monetization.items():
            report.append(f"\n{platform}:")
            for metric in metrics:
                report.append(
                    f"  {metric['metric']}: {metric['current']:,} / "
                    f"{metric['target']:,} ({metric['percentage']:.1f}%)"
                )
                
                # Progress bar
                bar_length = 30
                filled = int(bar_length * metric['percentage'] / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                report.append(f"  [{bar}]")
        
        return "\n".join(report)


def seed_sample_data():
    """Create sample analytics data for testing"""
    dashboard = AnalyticsDashboard()
    
    platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitch']
    
    # Seed 30 days of data
    for days_ago in range(30, -1, -1):
        date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        for i, platform in enumerate(platforms):
            # Simulate growth
            base_followers = (i + 1) * 100
            growth_factor = (30 - days_ago) * 10
            followers = base_followers + growth_factor + (i * 50)
            
            metrics = PlatformMetrics(
                platform=platform,
                date=date,
                followers=followers,
                posts_count=2 if days_ago < 14 else 1,
                impressions=followers * 10,
                reach=followers * 8,
                engagement_count=followers // 10,
                engagement_rate=min(5.0 + (i * 0.5), 10.0),
                profile_visits=followers // 5,
                clicks=followers // 20,
                video_views=followers * 3,
                new_followers=10 if days_ago < 14 else 5
            )
            
            dashboard.add_daily_metrics(metrics)
    
    # Add monetization tracking
    monetization_reqs = {
        'TikTok': [('followers', 250, 10000), ('views_30_days', 5000, 100000)],
        'YouTube': [('subscribers', 150, 1000), ('watch_hours', 500, 4000)],
        'Instagram': [('followers', 200, 10000)],
        'Twitch': [('followers', 45, 50), ('stream_hours', 6, 8)],
    }
    
    for platform, reqs in monetization_reqs.items():
        for metric_name, current, target in reqs:
            dashboard.update_monetization_progress(platform, metric_name, current, target)
    
    return dashboard


def main():
    """Initialize analytics dashboard"""
    print("Initializing Sisi Lola Analytics Dashboard...")
    
    dashboard = seed_sample_data()
    
    print("\nGenerated Dashboard Report:")
    print(dashboard.generate_dashboard_report())
    
    # Export to CSV
    export_dir = dashboard.export_to_csv()
    print(f"\n✓ Analytics exported to: {export_dir}")


if __name__ == "__main__":
    main()
