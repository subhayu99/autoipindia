from pydantic import BaseModel, Field, model_validator

from typing import Optional
from logic import search_application as sa
from logic import search_wordmark as sw

SCRAPED_FIELDS = ['application_number', 'wordmark', 'class_name', 'status']


class TrademarkSearchParams(BaseModel):
    """
    Trademark data class for handling trademark searches
    
    Attributes:
        wordmark: The trademark name/text
        class_name: Trademark class
        application_number: Official application number
    """
    wordmark: Optional[str] = Field(None, description="Trademark name/text. Required if application number is not provided")
    class_name: Optional[int] = Field(None, description="Trademark class. Required if application number is not provided")
    application_number: Optional[str] = Field(None, description="Official application number. Required if wordmark and class are not provided")
    
    @model_validator(mode='after')
    def validate_trademark(self):
        """Validate trademark data after initialization"""
        assert (self.wordmark and self.class_name) or self.application_number, "Either wordmark and class or application number must be provided"

    def search(self, headless: bool = True, max_retries: int = 3):
        """
        Search for trademark information
        
        Prioritizes search by wordmark and class if both are available, otherwise falls back to application number search.
        
        Args:
            headless: Whether to run browser in headless mode
            max_retries: Maximum number of retry attempts
            
        Returns:
            DataFrame with trademark information (fields: `SCRAPED_FIELDS`) or None if failed
        """
        df = None
        print(f"Searching for trademark with params: {self.to_dict()}")
        
        try:
            # Try wordmark search first if both wordmark and class are available
            if self.wordmark and self.class_name:
                print("Attempting wordmark search")
                df = sw.search_trademark(
                    self.wordmark, 
                    self.class_name, 
                    max_captcha_retries=max_retries,
                    headless=headless
                )
                print(f"Wordmark search result: {df if df is not None else 'None'}")
                
                # If application number is provided, filter results
                if self.application_number and df is not None and not df.empty:
                    print(f"Filtering results by application number: {self.application_number}")
                    _df = df[df['application_number'] == str(self.application_number)]
                    print(f"Filtered result: {_df if _df is not None else 'None'}")
                    
                    # If filtered results are not empty, use them
                    if not _df.empty:
                        df = _df
                        print("Using filtered result")
            
            # Fall back to application number search if wordmark search failed or not possible
            if self.application_number and (df is None or df.empty):
                print("Attempting application number search")
                df = sa.search_trademark(self.application_number, headless=headless)
                print(f"Application number search result: {df if df is not None else 'None'}")

        except Exception as e:
            print(f"Error during trademark search: {str(e)}")
            return None
        
        if df is not None and not df.empty:
            # Return only required fields                
            return df[SCRAPED_FIELDS]
    
    def to_dict(self) -> dict:
        """Convert trademark to dictionary"""
        return {
            'wordmark': self.wordmark,
            'class_name': self.class_name,
            'application_number': self.application_number
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrademarkSearchParams':
        """Create Trademark from dictionary"""
        return cls(
            wordmark=data.get('wordmark'),
            class_name=data.get('class_name'),
            application_number=data.get('application_number')
        )
    
    def __str__(self) -> str:
        """String representation of trademark"""
        parts = []
        if self.wordmark:
            parts.append(f"'{self.wordmark}'")
        if self.application_number:
            parts.append(f"App#{self.application_number}")
        if self.class_name:
            parts.append(f"Class {self.class_name}")
        return " | ".join(parts)