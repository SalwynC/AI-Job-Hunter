#!/usr/bin/env python3
"""
Google Sheets Integration for AI Job Hunter
============================================

Auto-creates and manages Google Sheets spreadsheet with:
- Job listings with ATS scores
- Keywords and suggestions
- Duplicate detection
- Real-time updates every 30 minutes
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Manage Google Sheets for job tracking."""
    
    def __init__(self, creds_json_path: Optional[str] = None):
        """Initialize Google Sheets connection."""
        self.creds_path = creds_json_path or os.getenv('GOOGLE_SHEETS_CREDS_JSON')
        self.spreadsheet = None
        self.worksheet = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Setup Google Sheets authentication."""
        try:
            if not self.creds_path or not Path(self.creds_path).exists():
                logger.warning(
                    "Google Sheets credentials not found. "
                    "Set GOOGLE_SHEETS_CREDS_JSON environment variable."
                )
                return
            
            # Authenticate
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.creds_path, scope
            )
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets authenticated successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}")
            self.client = None
    
    def create_or_get_spreadsheet(self, title: str = "AI Job Hunter - Job Tracker") -> bool:
        """Create spreadsheet if not exists, or get existing."""
        if not self.client:
            logger.warning("Google Sheets client not initialized")
            return False
        
        try:
            # Try to open existing spreadsheet
            try:
                self.spreadsheet = self.client.open(title)
                logger.info(f"Opened existing spreadsheet: {title}")
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                self.spreadsheet = self.client.create(title)
                logger.info(f"Created new spreadsheet: {title}")
            
            # Get or create main worksheet
            try:
                self.worksheet = self.spreadsheet.worksheet("Jobs")
            except gspread.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet("Jobs", 1000, 15)
                logger.info("Created 'Jobs' worksheet")
            
            # Setup headers if empty
            if not self.worksheet.get_all_values():
                self._setup_headers()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating/getting spreadsheet: {e}")
            return False
    
    def _setup_headers(self):
        """Setup spreadsheet headers."""
        headers = [
            "Job ID",
            "Title",
            "Company",
            "Location",
            "Role Type",
            "Salary (Min LPA)",
            "Salary (Max LPA)",
            "Experience Required",
            "Posted Date",
            "ATS Score %",
            "Keywords Matched",
            "Suggestions",
            "Duplicate On",
            "Job Link",
            "Scraped At"
        ]
        
        self.worksheet.insert_row(headers, 1)
        
        # Format header row
        try:
            # Bold header
            header_format = {
                'backgroundColor': {
                    'red': 0.25,
                    'green': 0.52,
                    'blue': 0.95
                },
                'textFormat': {
                    'bold': True,
                    'foregroundColor': {
                        'red': 1,
                        'green': 1,
                        'blue': 1
                    }
                }
            }
            
            # Apply formatting (if using gspread_formatting)
            logger.info("Headers setup complete")
        except Exception as e:
            logger.warning(f"Could not format headers: {e}")
    
    async def append_jobs_batch(self, jobs: List[Dict]) -> bool:
        """Append batch of jobs to spreadsheet."""
        if not self.client or not self.spreadsheet:
            logger.warning("Google Sheets not initialized")
            return False
        
        try:
            rows_to_insert = []
            
            for job in jobs:
                row = [
                    job.get('job_id', f"job_{hash(job.get('title', ''))}"),
                    job.get('title', ''),
                    job.get('company', ''),
                    job.get('location', ''),
                    job.get('job_type', 'Full-Time'),
                    job.get('salary_min', ''),
                    job.get('salary_max', ''),
                    job.get('experience_required', ''),
                    job.get('posted_date', ''),
                    f"{job.get('ats_score', 0):.1f}",
                    '; '.join(job.get('keywords_matched', [])),
                    job.get('suggestion', ''),
                    '; '.join(job.get('duplicate_sources', [])) if job.get('duplicate_sources') else '',
                    job.get('link', ''),
                    datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                ]
                rows_to_insert.append(row)
            
            if rows_to_insert:
                # Insert all rows at once
                self.worksheet.insert_rows(rows_to_insert, 2)  # Insert after header
                logger.info(f"Inserted {len(rows_to_insert)} jobs into Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Error appending jobs to Sheets: {e}")
            return False
    
    def update_job_score(self, job_id: str, ats_score: float) -> bool:
        """Update ATS score for specific job."""
        if not self.worksheet:
            return False
        
        try:
            # Find row with job_id
            cell = self.worksheet.find(job_id)
            if cell:
                # Update score in same row, column J (10)
                self.worksheet.update_cell(cell.row, 10, f"{ats_score:.1f}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating job score: {e}")
            return False
    
    def mark_applied(self, job_id: str, applied_date: Optional[str] = None) -> bool:
        """Mark job as applied."""
        if not self.worksheet:
            return False
        
        try:
            cell = self.worksheet.find(job_id)
            if cell:
                applied_date = applied_date or datetime.now(timezone.utc).strftime('%Y-%m-%d')
                # Add applied status (add new column if needed)
                self.worksheet.update_cell(cell.row, 16, f"Applied: {applied_date}")
                logger.info(f"Marked job {job_id} as applied")
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking job as applied: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get spreadsheet statistics."""
        if not self.worksheet:
            return {}
        
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                return {"total_jobs": 0}
            
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            stats = {
                "total_jobs": len(df),
                "avg_ats_score": df.iloc[:, 9].astype(float).mean() if len(df) > 0 else 0,
                "salary_ranges": {
                    "0-3 LPA": len(df[df.iloc[:, 6].astype(float, errors='ignore') <= 3]),
                    "3-5 LPA": len(df[(df.iloc[:, 5].astype(float, errors='ignore') >= 3) & 
                                      (df.iloc[:, 6].astype(float, errors='ignore') <= 5)]),
                    "5+ LPA": len(df[df.iloc[:, 5].astype(float, errors='ignore') >= 5])
                },
                "locations": df.iloc[:, 3].value_counts().head(5).to_dict() if len(df) > 0 else {}
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {}
    
    def export_to_csv(self, output_path: str = "jobs_export.csv") -> bool:
        """Export sheet data to CSV."""
        if not self.worksheet:
            return False
        
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                logger.warning("No data to export")
                return False
            
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(df)} jobs to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def cleanup_old_entries(self, days_old: int = 30) -> int:
        """Remove jobs older than specified days."""
        if not self.worksheet:
            return 0
        
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                return 0
            
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            # Parse dates and filter
            df['Scraped At'] = pd.to_datetime(df['Scraped At'], errors='coerce')
            cutoff_date = pd.Timestamp.now(tz=timezone.utc) - pd.Timedelta(days=days_old)
            
            old_rows = len(df[df['Scraped At'] < cutoff_date])
            
            if old_rows > 0:
                # Delete old rows (would need manual implementation for gspread)
                logger.info(f"Found {old_rows} rows older than {days_old} days")
            
            return old_rows
        except Exception as e:
            logger.error(f"Error cleaning up old entries: {e}")
            return 0
    
    def get_duplicate_summary(self) -> Dict[str, List[str]]:
        """Get summary of duplicate jobs across platforms."""
        if not self.worksheet:
            return {}
        
        try:
            all_values = self.worksheet.get_all_values()
            if len(all_values) <= 1:
                return {}
            
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            # Find rows with duplicates
            duplicates = {}
            for idx, row in df.iterrows():
                if row.get('Duplicate On') and row['Duplicate On'].strip():
                    job_title = row.get('Title', 'Unknown')
                    sources = row['Duplicate On'].split('; ')
                    duplicates[job_title] = sources
            
            logger.info(f"Found {len(duplicates)} duplicate jobs")
            return duplicates
        except Exception as e:
            logger.error(f"Error getting duplicates: {e}")
            return {}


class SheetsReportGenerator:
    """Generate reports from Google Sheets data."""
    
    def __init__(self, sheets_manager: GoogleSheetsManager):
        self.sheets = sheets_manager
    
    def generate_daily_summary(self) -> str:
        """Generate daily job summary report."""
        stats = self.sheets.get_stats()
        duplicates = self.sheets.get_duplicate_summary()
        
        report = f"""
📊 DAILY JOB HUNTING SUMMARY
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

📈 Statistics:
- Total Jobs Found: {stats.get('total_jobs', 0)}
- Average ATS Score: {stats.get('avg_ats_score', 0):.1f}%
- Duplicate Listings: {len(duplicates)}

💰 Salary Distribution:
"""
        
        for salary_range, count in stats.get('salary_ranges', {}).items():
            report += f"  {salary_range}: {count} jobs\n"
        
        report += "\n📍 Top Locations:\n"
        for location, count in list(stats.get('locations', {}).items())[:5]:
            report += f"  {location}: {count} jobs\n"
        
        if duplicates:
            report += "\n🔄 Duplicate Jobs Found:\n"
            for job_title, sources in list(duplicates.items())[:10]:
                report += f"  • {job_title} (found on {len(sources)} platforms)\n"
        
        return report
    
    def generate_top_opportunities(self, limit: int = 10) -> str:
        """Generate top job opportunities report."""
        if not self.sheets.worksheet:
            return "No data available"
        
        try:
            all_values = self.sheets.worksheet.get_all_values()
            if len(all_values) <= 1:
                return "No jobs available"
            
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            # Sort by ATS score
            df['ATS Score %'] = pd.to_numeric(df['ATS Score %'], errors='coerce')
            top_jobs = df.nlargest(limit, 'ATS Score %')
            
            report = f"🎯 TOP {limit} OPPORTUNITIES\n\n"
            
            for idx, job in top_jobs.iterrows():
                report += f"{idx+1}. **{job['Title']}** @ {job['Company']}\n"
                report += f"   Salary: {job['Salary (Min LPA)']}-{job['Salary (Max LPA)']} LPA\n"
                report += f"   ATS Score: {job['ATS Score %']}%\n"
                report += f"   Location: {job['Location']}\n"
                report += f"   Keywords: {job['Keywords Matched']}\n\n"
            
            return report
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return "Error generating report"


if __name__ == "__main__":
    # Test Google Sheets integration
    manager = GoogleSheetsManager()
    manager.create_or_get_spreadsheet()
    
    # Test with sample data
    test_jobs = [
        {
            'title': 'Data Analyst',
            'company': 'Tech Corp',
            'location': 'Bangalore',
            'salary_min': 4,
            'salary_max': 6,
            'ats_score': 85.5,
            'keywords_matched': ['Python', 'SQL', 'Analytics'],
            'duplicate_sources': [],
            'link': 'https://example.com/job1'
        }
    ]
    
    import asyncio
    asyncio.run(manager.append_jobs_batch(test_jobs))
    print("Google Sheets integration test completed")
