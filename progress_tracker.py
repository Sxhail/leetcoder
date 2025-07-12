"""
progress_tracker.py - Tracks LeetCode Blind 75 progress using Playwright and API queries.
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from playwright.async_api import async_playwright
import config

class ProgressTracker:
    """Tracks LeetCode Blind 75 progress."""
    
    def __init__(self, leetcode_session: str):
        self.leetcode_session = leetcode_session
        self.problems = self._load_problems()
        self.base_url = config.LEETCODE_BASE_URL
    
    def _load_problems(self) -> List[Dict]:
        """Load Blind 75 problems from JSON file."""
        try:
            with open(config.PROBLEMS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('problems', [])
        except Exception as e:
            print(f"❌ Error loading problems: {e}")
            return []
    
    async def get_user_submissions(self) -> List[Dict]:
        """Get user's recent submissions using GraphQL API."""
        import aiohttp
        
        try:
            # Extract username from session token (JWT decode)
            import jwt
            try:
                # Decode JWT token to get username
                decoded = jwt.decode(self.leetcode_session, options={"verify_signature": False})
                username = decoded.get('username', 'suhailjameel7')  # fallback to your username
                print(f"👤 Using username: {username}")
            except:
                username = 'suhailjameel7'  # fallback username
                print(f"👤 Using fallback username: {username}")
            
            # GraphQL query to get recent submissions
            graphql_query = """
            query recentAcSubmissionList($username: String!, $limit: Int!) {
                recentAcSubmissionList(username: $username, limit: $limit) {
                    id
                    title
                    titleSlug
                    timestamp
                    statusDisplay
                    lang
                }
            }
            """
            
            # Make direct HTTP request
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                data = {
                    'query': graphql_query,
                    'variables': {
                        'username': username,
                        'limit': 100
                    }
                }
                
                print(f"🌐 Making GraphQL request to {self.base_url}/graphql")
                async with session.post(
                    f"{self.base_url}/graphql",
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'data' in result and 'recentAcSubmissionList' in result['data']:
                            submissions = result['data']['recentAcSubmissionList']
                            print(f"✅ Found {len(submissions)} recent submissions")
                            return submissions
                        else:
                            print("❌ No submission data in response")
                            return []
                    else:
                        print(f"❌ HTTP {response.status}: {await response.text()}")
                        return []
                        
        except Exception as e:
            print(f"❌ Error fetching submissions: {e}")
            return []
    
    async def _extract_username(self, page) -> Optional[str]:
        """Extract username from LeetCode profile page."""
        try:
            # Try to get username from URL
            url = page.url
            if '/profile/' in url:
                username = url.split('/profile/')[-1].split('/')[0]
                if username and username != 'profile':
                    return username
            
            # Try to get from page content
            username_element = await page.query_selector('[data-cy="username"]')
            if username_element:
                return await username_element.text_content()
            
            return None
        except Exception:
            return None
    
    def get_solved_problems(self, submissions: List[Dict], target_date: datetime) -> List[str]:
        """Get list of problem slugs solved on the target date."""
        solved_slugs = []
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        for submission in submissions:
            if submission.get('statusDisplay') == 'Accepted':
                # Convert timestamp to date
                timestamp = int(submission.get('timestamp', 0))
                submission_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                
                if submission_date == target_date_str:
                    title_slug = submission.get('titleSlug')
                    if title_slug:
                        solved_slugs.append(title_slug)
        
        return list(set(solved_slugs))  # Remove duplicates
    
    def get_blind75_progress(self, solved_slugs: List[str]) -> Dict:
        """Get progress on Blind 75 problems."""
        blind75_slugs = {problem['slug'] for problem in self.problems}
        solved_blind75 = [slug for slug in solved_slugs if slug in blind75_slugs]
        
        return {
            'total_solved': len(solved_slugs),
            'blind75_solved': len(solved_blind75),
            'blind75_total': len(blind75_slugs),
            'solved_problems': solved_blind75
        }
    
    async def check_daily_progress(self, target_date: Optional[datetime] = None) -> Dict:
        """Check progress for a specific date (defaults to today)."""
        if target_date is None:
            target_date = datetime.now()
        
        print(f"📊 Checking progress for {target_date.strftime('%Y-%m-%d')}...")
        
        # Get user submissions
        submissions = await self.get_user_submissions()
        if not submissions:
            return {
                'date': target_date.strftime('%Y-%m-%d'),
                'total_solved': 0,
                'blind75_solved': 0,
                'blind75_total': len(self.problems),
                'solved_problems': [],
                'success': False
            }
        
        # Get solved problems for the target date
        solved_slugs = self.get_solved_problems(submissions, target_date)
        
        # Get Blind 75 progress
        progress = self.get_blind75_progress(solved_slugs)
        
        result = {
            'date': target_date.strftime('%Y-%m-%d'),
            'total_solved': progress['total_solved'],
            'blind75_solved': progress['blind75_solved'],
            'blind75_total': progress['blind75_total'],
            'solved_problems': progress['solved_problems'],
            'success': True
        }
        
        print(f"✅ Solved {progress['blind75_solved']} Blind 75 problems on {target_date.strftime('%Y-%m-%d')}")
        return result
    
    async def check_yesterday_progress(self) -> Dict:
        """Check progress for yesterday."""
        yesterday = datetime.now() - timedelta(days=1)
        return await self.check_daily_progress(yesterday)
    
    async def check_today_progress(self) -> Dict:
        """Check progress for today."""
        return await self.check_daily_progress(datetime.now())
    
    def get_next_unsolved_problem(self) -> Optional[Dict]:
        """Get the next unsolved Blind 75 problem."""
        # This would need to be called after getting current progress
        # For now, return the first problem
        if self.problems:
            return self.problems[0]
        return None

# Example usage
async def main():
    from auth_manager import AuthManager
    
    auth_manager = AuthManager()
    session = auth_manager.get_leetcode_session()
    
    if session:
        tracker = ProgressTracker(session)
        progress = await tracker.check_today_progress()
        print(f"Today's progress: {progress}")
    else:
        print("❌ LeetCode session not found")

if __name__ == "__main__":
    asyncio.run(main()) 