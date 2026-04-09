"""
Google Sheets Export Integration
Saves job data to Google Sheets with clickable links, formatting, and sortable filters
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleSheetsExporter:
    """Export job data to Google Sheets with advanced formatting and features"""
    
    def __init__(self):
        self.credentials_path = Path(__file__).parent.parent / ".credentials" / "google_sheets.json"
        self.sheet_id = None
        
    def load_credentials(self):
        """Load Google Sheets API credentials"""
        try:
            if not self.credentials_path.exists():
                logger.warning("Google Sheets credentials not found. Setup required.")
                return False
            
            with open(self.credentials_path, 'r') as f:
                self.credentials = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return False
    
    def create_job_sheet(self, df: pd.DataFrame, sheet_name: str = "Jobs") -> Dict[str, Any]:
        """Create sheet with jobs data and formatting"""
        
        # Clean and prepare data
        df_clean = df.copy()
        
        # Add hyperlink column for 'Apply Now'
        df_clean['apply_link'] = df_clean['link'].apply(
            lambda x: f'=HYPERLINK("{x}", "Apply")' if pd.notna(x) else ""
        )
        
        # Order columns logically
        columns_order = [
            'title', 'company', 'location', 'job_type', 
            'salary_text', 'source', 'score', 'apply_link',
            'experience_match', 'location_match', 'posted_date'
        ]
        
        available_cols = [col for col in columns_order if col in df_clean.columns]
        df_clean = df_clean[available_cols]
        
        # Rename for readability
        rename_map = {
            'title': 'Job Title',
            'company': 'Company',
            'location': 'Location',
            'job_type': 'Type',
            'salary_text': 'Salary',
            'source': 'Source',
            'score': 'Score',
            'apply_link': 'Apply',
            'experience_match': 'Exp Match',
            'location_match': 'Loc Match',
            'posted_date': 'Posted'
        }
        
        df_clean = df_clean.rename(columns=rename_map)
        
        return {
            'name': sheet_name,
            'data': df_clean,
            'rows': len(df_clean),
            'columns': len(df_clean.columns)
        }
    
    def create_summary_sheet(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary statistics sheet"""
        
        summary_data = {
            'Metric': [],
            'Value': []
        }
        
        for key, value in stats.items():
            summary_data['Metric'].append(str(key))
            summary_data['Value'].append(str(value))
        
        df = pd.DataFrame(summary_data)
        
        return {
            'name': 'Summary',
            'data': df,
            'rows': len(df),
            'columns': 2
        }
    
    def create_filtered_sheets(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create multiple filtered sheets by category"""
        
        sheets = []
        
        # By Source
        if 'source' in df.columns:
            for source in df['source'].unique():
                if pd.notna(source):
                    source_df = df[df['source'] == source].copy()
                    source_df['apply_link'] = source_df['link'].apply(
                        lambda x: f'=HYPERLINK("{x}", "Apply")' if pd.notna(x) else ""
                    )
                    
                    sheets.append({
                        'name': f'{source}({len(source_df)})',
                        'data': source_df,
                        'rows': len(source_df),
                        'columns': len(source_df.columns)
                    })
        
        # By Job Type
        if 'job_type' in df.columns:
            for job_type in df['job_type'].unique():
                if pd.notna(job_type):
                    type_df = df[df['job_type'] == job_type].copy()
                    sheets.append({
                        'name': f'{job_type}({len(type_df)})',
                        'data': type_df,
                        'rows': len(type_df),
                        'columns': len(type_df.columns)
                    })
        
        return sheets
    
    def create_high_score_sheet(self, df: pd.DataFrame, threshold: float = 7.0) -> Dict[str, Any]:
        """Create sheet with only high-scoring jobs"""
        
        if 'score' not in df.columns:
            df['score'] = 0
        
        high_score_df = df[df['score'] >= threshold].copy()
        high_score_df = high_score_df.sort_values('score', ascending=False)
        
        high_score_df['apply_link'] = high_score_df['link'].apply(
            lambda x: f'=HYPERLINK("{x}", "Apply")' if pd.notna(x) else ""
        )
        
        return {
            'name': f'High Score (≥{threshold})',
            'data': high_score_df,
            'rows': len(high_score_df),
            'columns': len(high_score_df.columns)
        }
    
    def export_to_csv_sheets(self, consolidated_df: pd.DataFrame, output_dir: Path = None):
        """Export comprehensive data to CSV files (local alternative to Google Sheets)"""
        
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "data" / "sheets_export"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main Jobs Sheet
        jobs_sheet = self.create_job_sheet(consolidated_df, "All Jobs")
        jobs_file = output_dir / f"01_All_Jobs_{timestamp}.csv"
        jobs_sheet['data'].to_csv(jobs_file, index=False)
        exports['All Jobs'] = str(jobs_file)
        logger.info(f"✅ Exported: {jobs_file}")
        
        # Summary Sheet
        stats = {
            'Total Jobs': len(consolidated_df),
            'Unique Companies': consolidated_df['company'].nunique() if 'company' in consolidated_df.columns else 0,
            'Unique Locations': consolidated_df['location'].nunique() if 'location' in consolidated_df.columns else 0,
            'Sources': consolidated_df['source'].nunique() if 'source' in consolidated_df.columns else 0,
            'Export Date': datetime.now().isoformat(),
        }
        summary_sheet = self.create_summary_sheet(stats)
        summary_file = output_dir / f"00_Summary_{timestamp}.csv"
        summary_sheet['data'].to_csv(summary_file, index=False)
        exports['Summary'] = str(summary_file)
        logger.info(f"✅ Exported: {summary_file}")
        
        # High Score Jobs
        high_score_sheet = self.create_high_score_sheet(consolidated_df, threshold=7.0)
        high_score_file = output_dir / f"02_High_Score_Jobs_{timestamp}.csv"
        high_score_sheet['data'].to_csv(high_score_file, index=False)
        exports['High Score'] = str(high_score_file)
        logger.info(f"✅ Exported: {high_score_file}")
        
        # By Source
        filtered_sheets = self.create_filtered_sheets(consolidated_df)
        for idx, sheet in enumerate(filtered_sheets):
            file_prefix = f"03_By_Source_" if 'source' in sheet['name'].lower() else f"04_By_Type_"
            safe_name = sheet['name'].replace('(', '_').replace(')', '').replace('/', '_').upper()
            sheet_file = output_dir / f"{file_prefix}{safe_name}_{timestamp}.csv"
            sheet['data'].to_csv(sheet_file, index=False)
            exports[sheet['name']] = str(sheet_file)
            logger.info(f"✅ Exported: {sheet_file}")
        
        # Top Companies
        if 'company' in consolidated_df.columns:
            top_companies = consolidated_df.groupby('company').size().sort_values(ascending=False).head(20)
            top_companies_df = pd.DataFrame({
                'Company': top_companies.index,
                'Job Count': top_companies.values
            })
            top_companies_file = output_dir / f"05_Top_Companies_{timestamp}.csv"
            top_companies_df.to_csv(top_companies_file, index=False)
            exports['Top Companies'] = str(top_companies_file)
            logger.info(f"✅ Exported: {top_companies_file}")
        
        # Statistics by Role
        if 'role' in consolidated_df.columns:
            role_stats = consolidated_df.groupby('role').agg({
                'title': 'count',
                'score': 'mean',
                'company': 'nunique'
            }).round(2)
            role_stats.columns = ['Total Jobs', 'Avg Score', 'Unique Companies']
            role_stats_file = output_dir / f"06_Stats_By_Role_{timestamp}.csv"
            role_stats.to_csv(role_stats_file)
            exports['Stats by Role'] = str(role_stats_file)
            logger.info(f"✅ Exported: {role_stats_file}")
        
        # Save export manifest
        manifest = {
            'export_date': datetime.now().isoformat(),
            'total_jobs': len(consolidated_df),
            'exports': exports,
            'output_directory': str(output_dir)
        }
        
        manifest_file = output_dir / f"manifest_{timestamp}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"📊 Export manifest: {manifest_file}")
        
        return exports
    
    def create_interactive_html(self, df: pd.DataFrame, output_path: Path = None) -> str:
        """Create an interactive HTML dashboard with sorting and filtering"""
        
        if output_path is None:
            output_path = Path(__file__).parent.parent / "data" / "jobs_dashboard.html"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df_clean = df.copy()
        df_clean['apply_link'] = df_clean['link'].apply(
            lambda x: f'<a href="{x}" target="_blank" class="btn-apply">Apply</a>' if pd.notna(x) else ""
        )
        
        # Sort by score descending
        if 'score' in df_clean.columns:
            df_clean = df_clean.sort_values('score', ascending=False)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Job Hunter - Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/datatables.net@1.13.6/js/jquery.dataTables.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/datatables.net-dt@1.13.6/css/jquery.dataTables.min.css">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    padding: 30px;
                }}
                
                header {{
                    margin-bottom: 30px;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 20px;
                }}
                
                h1 {{
                    color: #333;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .stat-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                
                .stat-card p {{
                    font-size: 0.9em;
                    opacity: 0.9;
                    margin-bottom: 10px;
                }}
                
                .stat-card .number {{
                    font-size: 2.5em;
                    font-weight: bold;
                }}
                
                .search-box {{
                    margin-bottom: 20px;
                }}
                
                .search-box input {{
                    width: 100%;
                    padding: 12px 15px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 1em;
                    transition: border-color 0.3s;
                }}
                
                .search-box input:focus {{
                    outline: none;
                    border-color: #667eea;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                
                th {{
                    background: #f5f5f5;
                    padding: 15px;
                    text-align: left;
                    font-weight: 600;
                    color: #333;
                    border-bottom: 2px solid #667eea;
                    cursor: pointer;
                }}
                
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                
                tr:hover {{
                    background: #f9f9f9;
                }}
                
                .score {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 0.9em;
                }}
                
                .score.high {{
                    background: #d4edda;
                    color: #155724;
                }}
                
                .score.medium {{
                    background: #fff3cd;
                    color: #856404;
                }}
                
                .score.low {{
                    background: #f8d7da;
                    color: #721c24;
                }}
                
                .btn-apply {{
                    display: inline-block;
                    padding: 8px 16px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 0.9em;
                    font-weight: 600;
                    transition: background 0.3s;
                }}
                
                .btn-apply:hover {{
                    background: #764ba2;
                    text-decoration: none;
                }}
                
                .dataTables_wrapper {{
                    margin-top: 20px;
                }}
                
                .dataTables_info {{
                    padding: 12px 0;
                    color: #666;
                }}
                
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: center;
                    color: #999;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🚀 AI Job Hunter Dashboard</h1>
                    <p style="color: #666; margin-top: 10px;">Your personal job opportunity tracker with AI-powered matching</p>
                </header>
                
                <div class="stats">
                    <div class="stat-card">
                        <p>Total Jobs</p>
                        <div class="number">{len(df_clean)}</div>
                    </div>
                    <div class="stat-card">
                        <p>Unique Companies</p>
                        <div class="number">{df_clean['company'].nunique() if 'company' in df_clean.columns else 0}</div>
                    </div>
                    <div class="stat-card">
                        <p>Job Sources</p>
                        <div class="number">{df_clean['source'].nunique() if 'source' in df_clean.columns else 0}</div>
                    </div>
                    <div class="stat-card">
                        <p>Avg Score</p>
                        <div class="number">{(df_clean['score'].mean() if 'score' in df_clean.columns else 0):.1f}</div>
                    </div>
                </div>
                
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Search jobs by title, company, location..." />
                </div>
                
                <table id="jobsTable" class="display" style="width:100%">
                    <thead>
                        <tr>
        """
        
        # Add table headers
        for col in df_clean.columns:
            if col != 'link':
                html_content += f"<th>{col}</th>"
        
        html_content += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add table rows
        for idx, row in df_clean.iterrows():
            html_content += "<tr>"
            for col in df_clean.columns:
                if col == 'link':
                    continue
                elif col == 'score':
                    score_val = row[col]
                    if isinstance(score_val, (int, float)):
                        if score_val >= 7:
                            score_class = 'high'
                        elif score_val >= 5:
                            score_class = 'medium'
                        else:
                            score_class = 'low'
                        html_content += f'<td><span class="score {score_class}">{score_val:.1f}</span></td>'
                    else:
                        html_content += f'<td>{row[col]}</td>'
                elif col == 'apply_link':
                    html_content += f'<td>{row[col]}</td>'
                else:
                    html_content += f'<td>{str(row[col])[:100]}</td>'
            html_content += "</tr>"
        
        html_content += """
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>📊 Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                    <p>💡 Tip: Click on column headers to sort, use search to filter jobs</p>
                </div>
            </div>
            
            <script>
                $(document).ready(function() {
                    var table = $('#jobsTable').DataTable({
                        "pageLength": 25,
                        "order": [[6, "desc"]],
                        "language": {
                            "search": "Filter results: "
                        }
                    });
                    
                    $('#searchInput').on('keyup', function() {
                        table.search(this.value).draw();
                    });
                });
            </script>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Created interactive dashboard: {output_path}")
        return str(output_path)


def consolidate_all_jobs(data_dir: Path = None) -> pd.DataFrame:
    """Consolidate jobs from all role folders"""
    
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"
    
    all_jobs = []
    
    # Look for jobs.csv in each role folder
    for role_dir in data_dir.glob("*/"):
        if role_dir.is_dir() and role_dir.name not in ['daily', 'monthly', 'sheets_export', 'tracking', 'excel', 'ai_handoff', 'apply_now', 'ci', 'logs', 'runs', 'runtime', 'scheduler', 'skills', 'telegram_bot']:
            jobs_file = role_dir / "jobs.csv"
            if jobs_file.exists():
                try:
                    df = pd.read_csv(jobs_file)
                    df['role'] = role_dir.name
                    all_jobs.append(df)
                    logger.info(f"✅ Loaded {len(df)} jobs from {role_dir.name}")
                except Exception as e:
                    logger.error(f"Failed to load {jobs_file}: {e}")
    
    if all_jobs:
        consolidated = pd.concat(all_jobs, ignore_index=True)
        # Remove duplicates by link
        consolidated = consolidated.drop_duplicates(subset=['link'], keep='first')
        return consolidated
    else:
        return pd.DataFrame()


if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Consolidate jobs
    logger.info("🔄 Consolidating all jobs...")
    consolidated_df = consolidate_all_jobs()
    
    if not consolidated_df.empty:
        logger.info(f"📊 Total jobs consolidated: {len(consolidated_df)}")
        
        # Export to sheets
        exporter = GoogleSheetsExporter()
        exports = exporter.export_to_csv_sheets(consolidated_df)
        
        # Create interactive dashboard
        dashboard_path = exporter.create_interactive_html(consolidated_df)
        logger.info(f"📈 Dashboard created: {dashboard_path}")
        
        logger.info("\n✅ All exports completed!")
        for name, path in exports.items():
            logger.info(f"  • {name}: {path}")
    else:
        logger.error("❌ No jobs found to consolidate")
