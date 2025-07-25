"""
Git Repository Activity Collector for DayLog
Tracks commits, branches, file changes, and coding sessions across all repositories
"""

import os
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import re


@dataclass
class GitActivity:
    """Represents a single Git activity"""
    timestamp: datetime
    activity_type: str  # 'commit', 'branch_switch', 'merge', 'file_change'
    repository: str
    branch: str
    commit_hash: Optional[str]
    commit_message: str
    author: str
    files_changed: List[str]
    insertions: int
    deletions: int
    repository_path: str


class GitCollector:
    """Collects Git activity from local repositories"""
    
    def __init__(self, settings):
        """Initialize Git collector with settings"""
        self.settings = settings
        self.project_directories = [
            self.settings.expand_path(path) 
            for path in self.settings.get('data_sources.git.project_directories', [])
        ]
        self.author_emails = self._get_author_emails()
    
    def _get_author_emails(self) -> List[str]:
        """Get author emails to filter commits (only your commits)"""
        emails = []
        
        try:
            # Get global git config email
            result = subprocess.run(
                ['git', 'config', '--global', 'user.email'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                emails.append(result.stdout.strip())
        except Exception:
            pass
        
        # Add common email patterns or let user configure
        configured_emails = self.settings.get('data_sources.git.author_emails', [])
        emails.extend(configured_emails)
        
        # If no emails found, we'll collect all commits
        return emails if emails else ['*']
    
    def collect(self, target_date: date) -> List[GitActivity]:
        """Collect Git activities for the specified date"""
        if not self.settings.is_enabled('git'):
            return []
        
        all_activities = []
        repositories_found = 0
        
        # Find all Git repositories
        for project_dir in self.project_directories:
            project_path = Path(project_dir)
            if not project_path.exists():
                continue
            
            # Find Git repositories in this directory
            git_repos = self._find_git_repositories(project_path)
            repositories_found += len(git_repos)
            
            for repo_path in git_repos:
                try:
                    repo_activities = self._collect_repository_activity(repo_path, target_date)
                    all_activities.extend(repo_activities)
                except Exception as e:
                    print(f"      ⚠️  Error processing {repo_path.name}: {str(e)}")
        
        print(f"   ⚙️ Git: Found {repositories_found} repositories, {len(all_activities)} activities")
        
        return sorted(all_activities, key=lambda x: x.timestamp)
    
    def _find_git_repositories(self, directory: Path) -> List[Path]:
        """Find all Git repositories in a directory tree"""
        git_repos = []
        
        try:
            # Check if current directory is a Git repo
            if (directory / '.git').exists():
                git_repos.append(directory)
            
            # Search subdirectories (limit depth to avoid performance issues)
            for item in directory.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check immediate subdirectories
                    if (item / '.git').exists():
                        git_repos.append(item)
                    
                    # Check one level deeper for common project structures
                    try:
                        for subitem in item.iterdir():
                            if subitem.is_dir() and (subitem / '.git').exists():
                                git_repos.append(subitem)
                    except (PermissionError, OSError):
                        continue
        
        except (PermissionError, OSError):
            pass
        
        return git_repos
    
    def _collect_repository_activity(self, repo_path: Path, target_date: date) -> List[GitActivity]:
        """Collect activity from a specific Git repository"""
        activities = []
        
        try:
            # Change to repository directory
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Get repository information
            repo_name = self._get_repository_name(repo_path)
            current_branch = self._get_current_branch()
            
            # Collect commits for the target date
            commits = self._get_commits_for_date(target_date)
            
            for commit_data in commits:
                # Filter by author if emails are configured
                if self.author_emails != ['*']:
                    if not any(email in commit_data['author_email'] for email in self.author_emails):
                        continue
                
                activity = GitActivity(
                    timestamp=commit_data['timestamp'],
                    activity_type='commit',
                    repository=repo_name,
                    branch=commit_data['branch'],
                    commit_hash=commit_data['hash'],
                    commit_message=commit_data['message'],
                    author=commit_data['author'],
                    files_changed=commit_data['files'],
                    insertions=commit_data['insertions'],
                    deletions=commit_data['deletions'],
                    repository_path=str(repo_path)
                )
                activities.append(activity)
            
            # Collect branch switches and merges if we have commits
            if activities:
                branch_activities = self._get_branch_activities(target_date, repo_name, str(repo_path))
                activities.extend(branch_activities)
        
        except Exception as e:
            print(f"      ❌ Git repo {repo_path.name}: {str(e)}")
        
        finally:
            try:
                os.chdir(original_cwd)
            except:
                pass
        
        return activities
    
    def _get_repository_name(self, repo_path: Path) -> str:
        """Get repository name from path or remote origin"""
        try:
            # Try to get remote origin URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract repo name from URL
                if '/' in url:
                    return url.split('/')[-1].replace('.git', '')
        except:
            pass
        
        # Fallback to directory name
        return repo_path.name
    
    def _get_current_branch(self) -> str:
        """Get current Git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return 'main'
    
    def _get_commits_for_date(self, target_date: date) -> List[Dict]:
        """Get all commits for a specific date"""
        commits = []
        
        try:
            # Calculate date range
            start_date = datetime.combine(target_date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            # Git log command with detailed format
            git_cmd = [
                'git', 'log',
                f'--since={start_date.isoformat()}',
                f'--until={end_date.isoformat()}',
                '--pretty=format:%H|%an|%ae|%ai|%s|%b',
                '--numstat'
            ]
            
            result = subprocess.run(git_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return commits
            
            # Parse the output
            commits = self._parse_git_log_output(result.stdout)
        
        except Exception as e:
            print(f"      ⚠️  Error getting commits: {str(e)}")
        
        return commits
    
    def _parse_git_log_output(self, output: str) -> List[Dict]:
        """Parse git log output into structured data"""
        commits = []
        lines = output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check if this is a commit line (contains hash|author|email|date|subject)
            if '|' in line:
                parts = line.split('|', 5)
                if len(parts) >= 5:
                    commit_hash = parts[0]
                    author = parts[1]
                    author_email = parts[2]
                    date_str = parts[3]
                    subject = parts[4]
                    body = parts[5] if len(parts) > 5 else ""
                    
                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        timestamp = timestamp.replace(tzinfo=None)  # Remove timezone for consistency
                    except:
                        timestamp = datetime.now()
                    
                    # Get file statistics
                    i += 1
                    files_changed = []
                    insertions = 0
                    deletions = 0
                    
                    # Parse numstat output (insertions, deletions, filename)
                    while i < len(lines) and lines[i].strip() and '|' not in lines[i]:
                        stat_line = lines[i].strip()
                        if '\t' in stat_line:
                            parts = stat_line.split('\t')
                            if len(parts) >= 3:
                                try:
                                    ins = int(parts[0]) if parts[0] != '-' else 0
                                    dels = int(parts[1]) if parts[1] != '-' else 0
                                    filename = parts[2]
                                    
                                    insertions += ins
                                    deletions += dels
                                    files_changed.append(filename)
                                except ValueError:
                                    pass
                        i += 1
                    
                    # Get current branch for this commit
                    branch = self._get_branch_for_commit(commit_hash)
                    
                    commit_data = {
                        'hash': commit_hash,
                        'author': author,
                        'author_email': author_email,
                        'timestamp': timestamp,
                        'message': f"{subject} {body}".strip(),
                        'branch': branch,
                        'files': files_changed,
                        'insertions': insertions,
                        'deletions': deletions
                    }
                    
                    commits.append(commit_data)
                    continue
            
            i += 1
        
        return commits
    
    def _get_branch_for_commit(self, commit_hash: str) -> str:
        """Get the branch that contains a specific commit"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--contains', commit_hash],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                for branch in branches:
                    branch = branch.strip()
                    if branch.startswith('* '):
                        return branch[2:]
                    elif branch and not branch.startswith('('):
                        return branch
        except:
            pass
        
        return self._get_current_branch()
    
    def _get_branch_activities(self, target_date: date, repo_name: str, repo_path: str) -> List[GitActivity]:
        """Get branch switching and merge activities"""
        activities = []
        
        try:
            # Get reflog for branch switches
            start_date = datetime.combine(target_date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            result = subprocess.run(
                ['git', 'reflog', '--date=iso', '--grep-reflog=checkout'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'checkout:' in line and 'moving from' in line:
                        # Parse reflog entry
                        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*moving from (\S+) to (\S+)', line)
                        if match:
                            timestamp_str = match.group(1)
                            from_branch = match.group(2)
                            to_branch = match.group(3)
                            
                            try:
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                if start_date <= timestamp < end_date:
                                    activity = GitActivity(
                                        timestamp=timestamp,
                                        activity_type='branch_switch',
                                        repository=repo_name,
                                        branch=to_branch,
                                        commit_hash=None,
                                        commit_message=f"Switched from {from_branch} to {to_branch}",
                                        author=self._get_git_user(),
                                        files_changed=[],
                                        insertions=0,
                                        deletions=0,
                                        repository_path=repo_path
                                    )
                                    activities.append(activity)
                            except:
                                pass
        
        except Exception:
            pass
        
        return activities
    
    def _get_git_user(self) -> str:
        """Get current Git user name"""
        try:
            result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "Unknown"
    
    def get_repository_summary(self, target_date: date) -> Dict[str, Any]:
        """Get a summary of Git activity across all repositories"""
        activities = self.collect(target_date)
        
        if not activities:
            return {
                'total_commits': 0,
                'repositories': [],
                'total_files_changed': 0,
                'total_insertions': 0,
                'total_deletions': 0,
                'branches_used': [],
                'most_active_repo': None
            }
        
        repositories = {}
        total_insertions = sum(a.insertions for a in activities)
        total_deletions = sum(a.deletions for a in activities)
        all_files = set()
        branches = set()
        
        for activity in activities:
            repo = activity.repository
            if repo not in repositories:
                repositories[repo] = {
                    'commits': 0,
                    'files_changed': set(),
                    'insertions': 0,
                    'deletions': 0,
                    'branches': set()
                }
            
            if activity.activity_type == 'commit':
                repositories[repo]['commits'] += 1
                repositories[repo]['files_changed'].update(activity.files_changed)
                repositories[repo]['insertions'] += activity.insertions
                repositories[repo]['deletions'] += activity.deletions
            
            repositories[repo]['branches'].add(activity.branch)
            branches.add(activity.branch)
            all_files.update(activity.files_changed)
        
        # Find most active repository
        most_active_repo = max(repositories.items(), key=lambda x: x[1]['commits']) if repositories else None
        
        return {
            'total_commits': len([a for a in activities if a.activity_type == 'commit']),
            'repositories': list(repositories.keys()),
            'total_files_changed': len(all_files),
            'total_insertions': total_insertions,
            'total_deletions': total_deletions,
            'branches_used': list(branches),
            'most_active_repo': most_active_repo[0] if most_active_repo else None,
            'repository_details': {
                repo: {
                    'commits': data['commits'],
                    'files_changed': len(data['files_changed']),
                    'insertions': data['insertions'],
                    'deletions': data['deletions'],
                    'branches': list(data['branches'])
                }
                for repo, data in repositories.items()
            }
        }
