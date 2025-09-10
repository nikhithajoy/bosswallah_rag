"""
Data loading and preprocessing utilities
"""
import pandas as pd
from typing import List, Dict, Any
from ..utils.constants import COURSE_LANGUAGE_MAPPING

class CourseDataLoader:
    """Handles loading and preprocessing of course data."""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
    
    def load_data(self) -> pd.DataFrame:
        """
        Load course data from CSV file.
        
        Returns:
            pd.DataFrame: Loaded course data
        """
        try:
            self.df = pd.read_csv(self.csv_path)
            return self.df
        except Exception as e:
            raise Exception(f"Failed to load data from {self.csv_path}: {str(e)}")
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the course data.
        
        Returns:
            pd.DataFrame: Preprocessed course data
        """
        if self.df is None:
            self.load_data()
        
        # Fill missing values
        self.df['Who This Course is For'] = self.df['Who This Course is For'].fillna("Not specified")
        
        # Strip whitespace from string columns
        self.df = self.df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Process language mappings
        self.df['Released Languages'] = self.df['Released Languages'].apply(
            self._map_languages
        )
        
        return self.df
    
    def _map_languages(self, cell) -> List[str]:
        """
        Map language codes to language names.
        
        Args:
            cell: Cell value containing language codes
            
        Returns:
            List[str]: List of language names
        """
        if pd.isna(cell):
            return ["English"]
        
        try:
            codes = str(cell).split(",")
            mapped_languages = []
            
            for code in codes:
                code = code.strip()
                if code.isdigit():
                    lang_name = COURSE_LANGUAGE_MAPPING.get(
                        int(code), 
                        f"Unknown-{code}"
                    )
                    mapped_languages.append(lang_name)
            
            return mapped_languages if mapped_languages else ["English"]
            
        except Exception:
            return ["English"]
    
    def get_course_by_id(self, course_id: int) -> Dict[str, Any]:
        """
        Get course information by course ID.
        
        Args:
            course_id (int): Course ID
            
        Returns:
            Dict[str, Any]: Course information
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        course_row = self.df[self.df['Course No'] == course_id]
        if course_row.empty:
            return {}
        
        return course_row.iloc[0].to_dict()
    
    def get_courses_by_language(self, language: str) -> List[Dict[str, Any]]:
        """
        Get courses available in a specific language.
        
        Args:
            language (str): Language name
            
        Returns:
            List[Dict[str, Any]]: List of courses
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        matching_courses = []
        for _, row in self.df.iterrows():
            if language in row['Released Languages']:
                matching_courses.append(row.to_dict())
        
        return matching_courses
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get dataset statistics.
        
        Returns:
            Dict[str, Any]: Dataset statistics
        """
        if self.df is None:
            return {}
        
        # Count courses by language
        language_counts = {}
        for _, row in self.df.iterrows():
            for lang in row['Released Languages']:
                language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total_courses': len(self.df),
            'unique_courses': self.df['Course No'].nunique(),
            'languages_supported': list(language_counts.keys()),
            'courses_by_language': language_counts,
            'columns': list(self.df.columns)
        }
    
    def search_courses(self, query: str, column: str = 'Course Title') -> List[Dict[str, Any]]:
        """
        Search courses by text query.
        
        Args:
            query (str): Search query
            column (str): Column to search in
            
        Returns:
            List[Dict[str, Any]]: Matching courses
        """
        if self.df is None:
            return []
        
        if column not in self.df.columns:
            return []
        
        mask = self.df[column].str.contains(query, case=False, na=False)
        matching_courses = self.df[mask]
        
        return matching_courses.to_dict('records')