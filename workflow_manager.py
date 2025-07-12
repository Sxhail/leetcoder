"""
workflow_manager.py - Guides the user to the next unsolved Blind 75 problem on NeetCode and LeetCode.
"""

import webbrowser
import json
from typing import Optional, Dict, List
import config

class WorkflowManager:
    """Manages the workflow for solving Blind 75 problems."""
    
    def __init__(self):
        self.problems = self._load_problems()
        self.neetcode_url = config.NEETCODE_BASE_URL
        self.leetcode_url = config.LEETCODE_BASE_URL
    
    def _load_problems(self) -> List[Dict]:
        """Load Blind 75 problems from JSON file."""
        try:
            with open(config.PROBLEMS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('problems', [])
        except Exception as e:
            print(f"❌ Error loading problems: {e}")
            return []
    
    def get_next_unsolved_problem(self, solved_problems: List[str]) -> Optional[Dict]:
        """Get the next unsolved Blind 75 problem."""
        for problem in self.problems:
            if problem['slug'] not in solved_problems:
                return problem
        return None
    
    def open_problem_on_neetcode(self, problem_slug: str) -> bool:
        """Open a problem on NeetCode.io."""
        try:
            neetcode_url = f"{self.neetcode_url}/problems/{problem_slug}"
            print(f"🔗 Opening {problem_slug} on NeetCode: {neetcode_url}")
            webbrowser.open(neetcode_url)
            return True
        except Exception as e:
            print(f"❌ Error opening NeetCode: {e}")
            return False
    
    def open_problem_on_leetcode(self, problem_slug: str) -> bool:
        """Open a problem on LeetCode.com."""
        try:
            leetcode_url = f"{self.leetcode_url}/problems/{problem_slug}"
            print(f"🔗 Opening {problem_slug} on LeetCode: {leetcode_url}")
            webbrowser.open(leetcode_url)
            return True
        except Exception as e:
            print(f"❌ Error opening LeetCode: {e}")
            return False
    
    def open_next_problem(self, solved_problems: List[str]) -> Optional[Dict]:
        """Open the next unsolved problem on both NeetCode and LeetCode."""
        next_problem = self.get_next_unsolved_problem(solved_problems)
        
        if not next_problem:
            print("🎉 Congratulations! You've solved all Blind 75 problems!")
            return None
        
        print(f"📝 Next problem: {next_problem['title']} ({next_problem['difficulty']})")
        print(f"📂 Category: {next_problem['category']}")
        
        # Open on NeetCode first
        self.open_problem_on_neetcode(next_problem['slug'])
        
        # Open on LeetCode
        self.open_problem_on_leetcode(next_problem['slug'])
        
        return next_problem
    
    def open_problem_by_slug(self, problem_slug: str) -> bool:
        """Open a specific problem by slug."""
        # Find the problem
        problem = None
        for p in self.problems:
            if p['slug'] == problem_slug:
                problem = p
                break
        
        if not problem:
            print(f"❌ Problem '{problem_slug}' not found in Blind 75 list")
            return False
        
        print(f"📝 Opening: {problem['title']} ({problem['difficulty']})")
        
        # Open on both platforms
        neetcode_success = self.open_problem_on_neetcode(problem_slug)
        leetcode_success = self.open_problem_on_leetcode(problem_slug)
        
        return neetcode_success and leetcode_success
    
    def get_problem_info(self, problem_slug: str) -> Optional[Dict]:
        """Get information about a specific problem."""
        for problem in self.problems:
            if problem['slug'] == problem_slug:
                return problem
        return None
    
    def list_remaining_problems(self, solved_problems: List[str]) -> List[Dict]:
        """List all remaining unsolved problems."""
        remaining = []
        for problem in self.problems:
            if problem['slug'] not in solved_problems:
                remaining.append(problem)
        return remaining
    
    def get_progress_summary(self, solved_problems: List[str]) -> Dict:
        """Get a summary of progress."""
        total_problems = len(self.problems)
        solved_count = len(solved_problems)
        remaining_count = total_problems - solved_count
        
        # Group by category
        category_progress = {}
        for problem in self.problems:
            category = problem['category']
            if category not in category_progress:
                category_progress[category] = {'total': 0, 'solved': 0}
            
            category_progress[category]['total'] += 1
            if problem['slug'] in solved_problems:
                category_progress[category]['solved'] += 1
        
        return {
            'total_problems': total_problems,
            'solved_count': solved_count,
            'remaining_count': remaining_count,
            'progress_percentage': (solved_count / total_problems) * 100 if total_problems > 0 else 0,
            'category_progress': category_progress
        }
    
    def suggest_next_problems(self, solved_problems: List[str], count: int = 3) -> List[Dict]:
        """Suggest the next few problems to solve."""
        remaining = self.list_remaining_problems(solved_problems)
        
        # Prioritize by difficulty (Easy first, then Medium, then Hard)
        difficulty_order = ['Easy', 'Medium', 'Hard']
        sorted_remaining = sorted(remaining, key=lambda x: difficulty_order.index(x['difficulty']))
        
        return sorted_remaining[:count]

# Example usage
if __name__ == "__main__":
    workflow = WorkflowManager()
    
    # Example: Get next problem (assuming none solved yet)
    next_problem = workflow.open_next_problem([])
    
    if next_problem:
        print(f"Next problem: {next_problem['title']}")
    
    # Example: Get progress summary
    summary = workflow.get_progress_summary([])
    print(f"Progress: {summary['solved_count']}/{summary['total_problems']} ({summary['progress_percentage']:.1f}%)") 